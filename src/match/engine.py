"""Deterministic match engine.

Contract
--------
    match(question: str, k: int = 10) -> dict

- Input: the student's question (free text).
- Output: one MatchResult dict (see docs/contracts.md) — query_id, the
  original question, and a top-k candidates list scored best-first.
- Deterministic: the same question against the same index always produces
  the same ranking. No LLM calls here — rationale generation lives in
  src/agent. v1 scoring is mean-of-profile-vectors cosine similarity.
- Match evidence is heuristic, per docs/contracts.md: matched_topics is the
  intersection of the query's extracted key terms with the candidate's
  topics_aggregate (empty list if no overlap); matched_work_ids is the
  candidate's most recent works, a stated recency heuristic.
"""


def match(question: str, k: int = 10) -> dict:
    """Rank researchers against a student question, returning a MatchResult. Stub."""
    raise NotImplementedError("stub: match engine not implemented yet")
