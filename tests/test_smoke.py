"""Smoke test: the API serves the contract when stub data is present.

Builds nothing — synthesizes a tiny DATA_DIR (two fake profiles plus a small
hand-made FAISS index; no embedding model needed, since the stub ranking
never queries the index vectors) and points the app at it before startup.
"""

import json

import faiss
import numpy as np
import pytest
from fastapi.testclient import TestClient


def _profile(n: int, name: str, topics: list[str]) -> dict:
    return {
        "author_id": f"https://openalex.org/A{n:010d}",
        "name": name,
        "affiliation": "Carnegie Mellon University",
        "works": [
            {
                "work_id": f"https://openalex.org/W{n:010d}",
                "title": f"A Study of {topics[0]}",
                "abstract": "Placeholder abstract.",
                "year": 2023,
                "topics": topics,
                "source_id": "openalex",
                "fetched_at": "2026-07-19T00:00:00Z",
            }
        ],
        "topics_aggregate": topics,
        "profile_updated_at": "2026-07-19T00:00:00Z",
    }


@pytest.fixture()
def client(tmp_path, monkeypatch):
    profiles = [
        _profile(1, "Ada Fakeworth", ["machine learning systems"]),
        _profile(2, "Boris Placeholder", ["differential privacy"]),
    ]
    (tmp_path / "profiles.json").write_text(json.dumps(profiles), encoding="utf-8")

    index = faiss.IndexFlatIP(8)
    index.add(np.eye(len(profiles), 8, dtype="float32"))
    faiss.write_index(index, str(tmp_path / "index.faiss"))

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from src.api.app import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


def test_match_returns_ranked_answer(client):
    response = client.post("/match", json={"question": "who works on ML systems?"})
    assert response.status_code == 200
    body = response.json()
    assert body["results"], "expected non-empty results"
    first = body["results"][0]
    assert first["rank"] == 1
    assert first["author_id"]
    assert "rationale" in first
    assert "grounded_citations" in first
    assert first["web_enrichment"] == []
    assert body["search_effort_used"] == "off"
    assert body["degraded_mode"] is False


def test_empty_question_returns_400(client):
    response = client.post("/match", json={"question": ""})
    assert response.status_code == 400
    assert response.json()["error"] == "empty_question"
