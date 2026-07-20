# CMU Research Matchmaker

A service that matches CMU students to faculty researchers based on published
work. It ingests publication data from the [OpenAlex API](https://openalex.org/),
builds researcher profiles, and ranks faculty against a student's stated
interests using embeddings and a FAISS vector index. Results come back as a
ranked list where every match carries a rationale grounded in — and cited
against — the actual publications it was derived from. Built for 95-731
(AI, Cloud, and DevOps), served via FastAPI in Docker.

## Quickstart

Prerequisites: Docker and either VS Code with the Dev Containers extension or
any devcontainer-compatible editor.

```bash
git clone <repo-url> cmu-research-matchmaker
cd cmu-research-matchmaker
```

Then either:

- **Devcontainer (recommended):** open the folder in VS Code and choose
  "Reopen in Container". The devcontainer builds the same image used
  everywhere else and drops you into it.
- **Plain Docker:**

  ```bash
  docker build -t cmu-research-matchmaker .
  docker run --rm -p 8000:8000 cmu-research-matchmaker
  ```

The API is then at `http://localhost:8000` — `POST /match` with a student
interest query returns ranked matches; `GET /health` returns `{"status": "ok"}`.

> **Note:** the Dockerfile and devcontainer config are not in the repo yet
> (next step in the scaffold). Until they land, the commands above won't run.

## Repo structure

| Path            | Role |
| --------------- | ---- |
| `src/adapters/` | Source adapters. OpenAlex is the real one; other sources are stubs returning contract-shaped data. |
| `src/ingest/`   | Ingestion pipeline. Pulls from adapters and stamps provenance (`source_id`, `fetched_at`, `trust_tier`) on every record. |
| `src/profiles/` | Profile builder. Aggregates ingested records into per-researcher profiles. |
| `src/match/`    | Matching. Embeddings, the FAISS vector store, and the deterministic match engine that produces the ranking. |
| `src/agent/`    | Agent runtime. Generates grounded, cited template rationales from matched profile data, behind a swappable AgentRuntime interface. |
| `src/api/`      | FastAPI app. `POST /match` (rank + rationales) and `GET /health`. |
| `docs/`         | `architecture.md` (system design) and `contracts.md` (the JSON shapes passed between layers). |
| `tests/`        | Test suite. |
| `PROVENANCE.md` | Log of human vs. AI-generated code, per course policy. |

## Conventions

1. **The container is the unit of truth.** The same image runs locally and in
   AWS. Nothing runs outside Docker — no "works on my machine" Python
   environments; if it isn't reproducible in the container, it doesn't count.
2. **Every module is stubbed before it's real.** A module that returns
   hardcoded contract-shaped data is a valid commit. Contracts (see
   `docs/contracts.md`) are agreed first; implementations fill in behind them.
3. **Provenance is stamped at ingestion time.** Every record gets `source_id`,
   `fetched_at`, and `trust_tier` in `src/ingest/`, exactly once. Downstream
   layers carry these fields forward and never invent or overwrite them.
4. **Human vs. AI authorship is logged.** All human- and AI-generated code is
   recorded in `PROVENANCE.md` per course policy — what was generated, how AI
   was used, and whether the team has reviewed it.
5. **The ingestion corpus is bounded.** Works published 2021 or later, from
   2–3 departments (approximately 100 authors), capped at the 20 most recent
   works per author. The department cut is implemented via a seeded author
   list, since OpenAlex does not filter by department.
6. **Data is baked in at build time.** Ingestion and embedding run at
   `docker build` time and the FAISS index ships inside the image, so a fresh
   clone plus `docker build && docker run` serves without a separate data
   step.
