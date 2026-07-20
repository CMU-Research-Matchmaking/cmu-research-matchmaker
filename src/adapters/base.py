"""Adapter contract shared by every source adapter.

Contract
--------
An adapter exposes one entry point:

    fetch(query: dict) -> list[dict]

- Input: a source-agnostic query (e.g. institution id, author name, topic).
- Output: a list of RawRecord dicts (see docs/contracts.md). Records are
  returned as fetched from the source — no provenance fields yet; those are
  stamped by the ingest layer, not here.
- Adapters never write to disk or to the vector store; they only fetch.
"""


def fetch(query: dict) -> list[dict]:
    """Fetch raw records matching the query. Stub."""
    raise NotImplementedError("stub: implement in a concrete adapter")
