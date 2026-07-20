"""Data-prep entrypoint, run at docker build time.

    python -m src.ingest.build_index [out_dir]

Writes to out_dir (default /build/data):

    profiles.json — ResearcherProfile[] (see docs/contracts.md)
    index.faiss   — FAISS index with one mean-of-works vector per profile,
                    L2-normalized, inner-product metric (= cosine). Row i of
                    the index corresponds to profiles[i] in profiles.json.

v1 state: FAKE_PROFILES below is a small hardcoded, clearly-fake set so the
full build-and-serve path works end to end. Real OpenAlex ingestion
(adapters -> ingest.pipeline -> profiles.builder) replaces FAKE_PROFILES
inside this entrypoint later; the Dockerfile does not change.
"""

import json
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_OUT_DIR = "/build/data"
FAKE_FETCHED_AT = "2026-07-19T00:00:00Z"


def _fake_work(num: int, title: str, abstract: str, year: int, topics: list[str]) -> dict:
    return {
        "work_id": f"https://openalex.org/W{num:010d}",
        "title": title,
        "abstract": abstract,
        "year": year,
        "topics": topics,
        "source_id": "openalex",
        "fetched_at": FAKE_FETCHED_AT,
    }


FAKE_PROFILES = [
    {
        "author_id": "https://openalex.org/A0000000001",
        "name": "Ada Fakeworth",
        "affiliation": "Carnegie Mellon University",
        "works": [
            _fake_work(11, "Scaling Distributed Training of Sparse Neural Networks", "We present a scheduler that shards sparse gradient updates across heterogeneous GPU clusters.", 2023, ["machine learning systems", "distributed training"]),
            _fake_work(12, "Compiler Passes for Quantized Inference on Edge Devices", "A compilation pipeline that lowers quantized transformer blocks to microcontroller targets.", 2024, ["ML compilers", "edge inference"]),
        ],
        "topics_aggregate": ["machine learning systems", "distributed training", "ML compilers", "edge inference"],
        "profile_updated_at": FAKE_FETCHED_AT,
    },
    {
        "author_id": "https://openalex.org/A0000000002",
        "name": "Boris Placeholder",
        "affiliation": "Carnegie Mellon University",
        "works": [
            _fake_work(21, "Differential Privacy Budgets for Longitudinal Health Data", "We derive tighter composition bounds for repeated queries over patient cohorts.", 2022, ["differential privacy", "health data"]),
            _fake_work(22, "Auditing Membership Inference Under Distribution Shift", "An audit framework showing privacy attacks weaken predictably as deployment data drifts.", 2024, ["privacy auditing", "membership inference"]),
        ],
        "topics_aggregate": ["differential privacy", "health data", "privacy auditing", "membership inference"],
        "profile_updated_at": FAKE_FETCHED_AT,
    },
    {
        "author_id": "https://openalex.org/A0000000003",
        "name": "Carmen Stubbs",
        "affiliation": "Carnegie Mellon University",
        "works": [
            _fake_work(31, "Screen-Reader-First Design Patterns for Data Dashboards", "A study of how blind analysts navigate charts, with derived interaction patterns.", 2023, ["accessibility", "human-computer interaction"]),
            _fake_work(32, "Co-Designing Voice Interfaces with Older Adults", "Participatory design sessions yielding guidelines for conversational agents in aging-in-place settings.", 2021, ["voice interfaces", "participatory design"]),
        ],
        "topics_aggregate": ["accessibility", "human-computer interaction", "voice interfaces", "participatory design"],
        "profile_updated_at": FAKE_FETCHED_AT,
    },
    {
        "author_id": "https://openalex.org/A0000000004",
        "name": "Devi Mockler",
        "affiliation": "Carnegie Mellon University",
        "works": [
            _fake_work(41, "Terrain-Adaptive Gait Planning for Quadruped Robots", "A model-predictive controller that replans footholds from proprioceptive slip signals.", 2024, ["legged robotics", "motion planning"]),
            _fake_work(42, "Sim-to-Real Transfer for Warehouse Manipulation", "Domain randomization curricula that close the reality gap for bin-picking arms.", 2022, ["sim-to-real", "manipulation"]),
        ],
        "topics_aggregate": ["legged robotics", "motion planning", "sim-to-real", "manipulation"],
        "profile_updated_at": FAKE_FETCHED_AT,
    },
]


def _work_text(work: dict) -> str:
    return f"{work['title']}. {work['abstract']} Topics: {', '.join(work['topics'])}"


def build(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(MODEL_NAME)
    profile_vectors = []
    for profile in FAKE_PROFILES:
        work_vectors = model.encode(
            [_work_text(w) for w in profile["works"]], normalize_embeddings=True
        )
        mean = np.asarray(work_vectors, dtype="float32").mean(axis=0)
        profile_vectors.append(mean / np.linalg.norm(mean))

    matrix = np.vstack(profile_vectors).astype("float32")
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)

    faiss.write_index(index, str(out / "index.faiss"))
    (out / "profiles.json").write_text(
        json.dumps(FAKE_PROFILES, indent=2), encoding="utf-8"
    )
    print(f"build_index: wrote {len(FAKE_PROFILES)} profiles and a dim-{matrix.shape[1]} index to {out}")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT_DIR)
