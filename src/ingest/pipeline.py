"""Ingestion pipeline with provenance tagging.

Contract
--------
    ingest(records: list[dict], source_id: str, trust_tier: str) -> list[dict]

- Input: raw records from an adapter, plus the source identity.
- Output: the same records with provenance fields stamped at ingestion time:
    source_id   — which adapter/source produced the record
    fetched_at  — UTC ISO-8601 timestamp of the fetch
    trust_tier  — "curated" for publication data, "live-unverified" for
                  anything pulled live from the web
- Provenance is stamped exactly once, here. Downstream layers (profiles,
  match, agent) must never invent or overwrite these fields.
"""


def ingest(records: list[dict], source_id: str, trust_tier: str) -> list[dict]:
    """Stamp provenance onto raw records. Stub."""
    raise NotImplementedError("stub: provenance stamping not implemented yet")
