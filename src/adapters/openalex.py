"""OpenAlex adapter — the one real (non-stubbed) source.

Contract
--------
    fetch_works(institution_id: str, since: str | None = None) -> list[dict]

- Queries the OpenAlex Works API (https://api.openalex.org/works) filtered to
  authors affiliated with the given institution (CMU: I74973139).
- Returns a list of RawRecord dicts (see docs/contracts.md), one per work,
  preserving OpenAlex ids so provenance can point back to the source.
- Handles OpenAlex cursor pagination internally; callers get the full result.
- No provenance stamping here — that happens in src/ingest.
"""


def fetch_works(institution_id: str, since: str | None = None) -> list[dict]:
    """Fetch works for an institution from OpenAlex. Stub."""
    raise NotImplementedError("stub: OpenAlex fetch not implemented yet")
