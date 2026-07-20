"""Agent runtime — rationale generation.

Contract (the AgentRuntime interface)
--------
    run(match_result: dict, profiles: list[dict]) -> dict

- Input: the deterministic MatchResult from src/match/engine.py plus the
  candidate ResearcherProfile dicts.
- Output: one RankedAnswer dict (see docs/contracts.md) — the same ranking,
  each result annotated with a rationale and grounded_citations built ONLY
  from that candidate's matched_topics / matched_work_ids. web_enrichment is
  always present as a key and always empty in this version.
- Ranking order is never changed here.
- The shipped v1 implementation is the template rationale generator in
  src/agent/fallback.py — that is the design, not a degraded mode. The
  interface is a deliberate seam: an LLM-backed runtime could be a second
  implementation behind it later, but none is planned or pending.
"""


def run(match_result: dict, profiles: list[dict]) -> dict:
    """Produce a RankedAnswer with grounded, cited rationales. Stub."""
    raise NotImplementedError("stub: agent runtime not implemented yet")
