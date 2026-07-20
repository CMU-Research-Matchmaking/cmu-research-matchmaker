"""Template rationale generator — the v1 design.

(The filename survives from an earlier Track A/B framing; per the team
amendments, the template rationale IS the design, not a fallback awaiting
a model decision.)

Contract (implements the AgentRuntime interface)
--------
    run(match_result: dict, profiles: list[dict]) -> dict

- Same signature and RankedAnswer output shape as src/agent/runtime.py.
- Builds a deterministic template rationale for each candidate from that
  candidate's own matched_topics / matched_work_ids — no LLM calls, no web
  calls.
- search_effort_used is always "off" and degraded_mode is always false in
  this version; the fields exist so the response shape would not change if
  enrichment were ever added.
"""


def run(match_result: dict, profiles: list[dict]) -> dict:
    """Template-based RankedAnswer for match results. Stub."""
    raise NotImplementedError("stub: template rationale generator not implemented yet")
