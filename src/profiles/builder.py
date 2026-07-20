"""Researcher profile builder.

Contract
--------
    build_profiles(records: list[dict]) -> list[dict]

- Input: provenance-stamped RawRecord dicts from the ingest layer.
- Output: ResearcherProfile dicts (see docs/contracts.md), one per faculty
  researcher, aggregating their works, topics, and venues.
- Profiles carry forward the provenance of every record they were built from,
  so any claim in a downstream rationale can be traced to a source.
"""


def build_profiles(records: list[dict]) -> list[dict]:
    """Aggregate raw records into researcher profiles. Stub."""
    raise NotImplementedError("stub: profile building not implemented yet")
