# Data Contracts

JSON shapes exchanged between layers. Every module consumes and produces
these shapes and nothing else. Everything upstream of `ResearcherProfile`
and everything downstream of `MatchResult` is fully decoupled by these
contracts — build your side to match the shape, not to match the other
person's code.

## RawRecord

Output of every source adapter, regardless of source:

```json
{
  "source_id": "openalex",
  "external_id": "https://openalex.org/W2741809807",
  "record_type": "work",
  "fetched_at": "2026-07-18T12:00:00Z",
  "trust_tier": "curated",
  "payload": { "note": "source-specific raw fields go here, untouched" }
}
```

## ResearcherProfile

Output of the profile builder; input to embedding and matching:

```json
{
  "author_id": "https://openalex.org/A5023888391",
  "name": "string",
  "affiliation": "string",
  "works": [
    {
      "work_id": "string",
      "title": "string",
      "abstract": "string",
      "year": 2025,
      "topics": ["string"],
      "source_id": "openalex",
      "fetched_at": "2026-07-18T12:00:00Z"
    }
  ],
  "topics_aggregate": ["string"],
  "profile_updated_at": "2026-07-18T12:00:00Z"
}
```

## MatchResult

Output of the match engine. **This is the seam between the two halves of
the system:**

```json
{
  "query_id": "uuid",
  "query": "string — the student's original question",
  "candidates": [
    {
      "author_id": "string",
      "name": "string",
      "score": 0.83,
      "matched_topics": ["string"],
      "matched_work_ids": ["string"]
    }
  ],
  "generated_at": "2026-07-18T12:00:00Z"
}
```

### v1 evidence population

- `matched_topics` — the intersection of the query's extracted key terms
  with the candidate's `topics_aggregate`; an empty list if no overlap.
- `matched_work_ids` — the candidate's most recent works, a stated recency
  heuristic.

Exact attribution arrives with per-paper multi-vector matching; the fields
exist now so the contract shape never changes.

## RankedAnswer

Output of the agent runtime + rationale module; input to the API layer:

```json
{
  "query_id": "uuid",
  "degraded_mode": false,
  "search_effort_used": "off",
  "results": [
    {
      "author_id": "string",
      "name": "string",
      "rank": 1,
      "rationale": "grounded explanation, built only from matched_topics / matched_work_ids",
      "grounded_citations": [{ "work_id": "string", "title": "string" }],
      "web_enrichment": [
        {
          "claim": "string",
          "source_url": "string",
          "fetched_at": "2026-07-18T12:00:00Z",
          "verified": false
        }
      ]
    }
  ]
}
```

`web_enrichment` is always present as a key on every result, just empty when
the web adapter is off. The response shape never changes between search
on/off — nothing downstream ever has to branch on which mode the backend
happened to be running in.

`search_effort_used` is always `"off"` and `degraded_mode` is always `false`
in this version; the fields exist so the response shape would not change if
web enrichment were added.

## API: POST /match

Student-facing:
`POST /match` — request `{ "question": "string" }` → response is a
`RankedAnswer`.

### Error contract

| Condition | Status | Body |
|---|---|---|
| Missing or empty `question` | 400 | `{ "error": "empty_question", "message": "string" }` |
| Malformed JSON body | 400 | `{ "error": "malformed_request", "message": "string" }` |
| Index not loaded / no profiles available | 503 | `{ "error": "index_unavailable", "message": "string" }` |
| Unhandled internal failure | 500 | `{ "error": "internal", "message": "string" }` |

All error bodies share one shape:
`{ "error": "machine_readable_code", "message": "human sentence" }`.
