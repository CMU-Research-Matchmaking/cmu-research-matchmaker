"""FastAPI application — the service entry point.

Contract
--------
    POST /match
        Request body: { "question": "string" }
        Response 200: a RankedAnswer (see docs/contracts.md). The response
        shape never changes regardless of backend configuration.
        Errors (per the contract table in docs/contracts.md), all shaped
        { "error": "code", "message": "string" }:
            400 empty_question, 400 malformed_request,
            503 index_unavailable, 500 internal.

    GET /health
        Response 200: {"status": "ok"} — used by Docker/AWS health checks.

Startup loads the FAISS index and profiles.json from DATA_DIR (default
/app/data, baked into the image at docker build time by
src.ingest.build_index). If either file is missing the service still starts,
and every /match call returns 503 index_unavailable.

Implementation status: validation, data loading, and the error contract are
real. Ranking is a stub — results are the first min(5, len(profiles))
profiles in stored order, with template rationales built from each profile's
own topics and works (contract-shaped data per repo convention 2).
match.engine + the agent runtime replace the body of _stub_ranked_answer;
nothing about the routes or contract changes.
"""

import json
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import faiss
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class MatchRequest(BaseModel):
    # Optional so a missing field reaches the endpoint and maps to
    # empty_question; malformed bodies fail validation -> malformed_request.
    question: str | None = None


def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": code, "message": message})


@asynccontextmanager
async def _lifespan(app: FastAPI):
    data_dir = Path(os.environ.get("DATA_DIR", "/app/data"))
    index_path = data_dir / "index.faiss"
    profiles_path = data_dir / "profiles.json"
    app.state.index = None
    app.state.profiles = None
    if index_path.exists() and profiles_path.exists():
        app.state.index = faiss.read_index(str(index_path))
        app.state.profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    yield


def _stub_ranked_answer(question: str, profiles: list[dict]) -> dict:
    results = []
    for rank, profile in enumerate(profiles[:5], start=1):
        works = profile.get("works", [])
        topics = profile.get("topics_aggregate", [])
        rationale = f"{profile['name']} works on {', '.join(topics[:3]) or 'their research area'}"
        if works:
            rationale += f'; recent work includes "{works[0]["title"]}"'
        results.append(
            {
                "author_id": profile["author_id"],
                "name": profile["name"],
                "rank": rank,
                "rationale": rationale + ".",
                "grounded_citations": [
                    {"work_id": w["work_id"], "title": w["title"]} for w in works[:2]
                ],
                "web_enrichment": [],
            }
        )
    return {
        "query_id": str(uuid.uuid4()),
        "degraded_mode": False,
        "search_effort_used": "off",
        "results": results,
    }


def create_app() -> FastAPI:
    app = FastAPI(title="CMU Research Matchmaker", lifespan=_lifespan)

    @app.exception_handler(RequestValidationError)
    async def _malformed(request: Request, exc: RequestValidationError):
        return _error(
            400,
            "malformed_request",
            'Request body must be valid JSON of the form {"question": "string"}.',
        )

    @app.exception_handler(Exception)
    async def _internal(request: Request, exc: Exception):
        return _error(500, "internal", "Unhandled internal failure.")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/match")
    async def match(body: MatchRequest, request: Request):
        if body.question is None or not body.question.strip():
            return _error(400, "empty_question", "The 'question' field is required and must be non-empty.")
        profiles = request.app.state.profiles
        if request.app.state.index is None or not profiles:
            return _error(503, "index_unavailable", "Index or profile data not loaded; rebuild the image.")
        return _stub_ranked_answer(body.question, profiles)

    return app


app = create_app()
