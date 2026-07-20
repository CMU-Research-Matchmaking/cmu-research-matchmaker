"""FastAPI application — the service entry point.

Contract
--------
Exposes:

    POST /match
        Request body: { "question": "string" }
        Response 200: a RankedAnswer (see docs/contracts.md). The response
        shape never changes regardless of backend configuration.
        Errors: see the error contract in docs/contracts.md — all error
        bodies are { "error": "code", "message": "string" }.
        Pipeline: match.engine.match() for the deterministic MatchResult,
        then the agent runtime (template rationale generator — the v1
        design) for the grounded, cited rationales.

    GET /health
        Response 200: {"status": "ok"} — used by Docker/AWS health checks.

The FastAPI app object will be defined here as `app` once dependencies are
added; run it with `uvicorn src.api.app:app` inside the container.
"""


def create_app():
    """Build and return the FastAPI app. Stub."""
    raise NotImplementedError("stub: FastAPI app not implemented yet")
