"""Web search adapter (SerpAPI by default; swappable).

Contract
--------
    search(query: str) -> list[dict]

- Returns web results for the query. Every result the agent uses downstream
  is tagged trust_tier "live-unverified" and must carry its source_url and
  fetched_at into RankedAnswer.web_enrichment.
- Stubbed off in v1 (search_effort "off"): returns an empty list. Turning
  search on later changes nothing about the RankedAnswer shape —
  web_enrichment just stops being empty.
- Swappable behind this interface: if Bedrock's native web tooling turns out
  to be available, it's a drop-in second implementation, not a rewrite.
"""


def search(query: str) -> list[dict]:
    """Search the web for the query. Stubbed off in v1."""
    return []
