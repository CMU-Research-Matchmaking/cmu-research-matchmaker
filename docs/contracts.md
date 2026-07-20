# Data Contracts

JSON shapes exchanged between layers. Every module consumes and produces
these shapes and nothing else.

## RawRecord

<!-- JSON shape TBD -->

## ResearcherProfile

<!-- JSON shape TBD -->

## MatchResult

<!-- JSON shape TBD -->

### Match evidence (v1 population rules)

The v1 match engine scores by cosine similarity against a mean-of-profile
vector, which cannot identify the specific topics or works that drove a
match. The evidence fields are therefore populated heuristically:

- `matched_topics` — the intersection of the query's extracted key terms
  with the candidate's `topics_aggregate`; an empty list if no overlap.
- `matched_work_ids` — the candidate's most recent works, a stated recency
  heuristic.

## RankedAnswer

<!-- JSON shape TBD -->

In this version `search_effort_used` is always `"off"` and `degraded_mode`
is always `false`. The fields exist so the response shape would not change
if enrichment were added.

## API: POST /match

<!-- Happy path: request { "question": "string" } → response is a RankedAnswer -->

### Error contract

| Condition | Status | Body |
|---|---|---|
| Missing or empty `question` | 400 | `{ "error": "empty_question", "message": "string" }` |
| Malformed JSON body | 400 | `{ "error": "malformed_request", "message": "string" }` |
| Index not loaded / no profiles available | 503 | `{ "error": "index_unavailable", "message": "string" }` |
| Unhandled internal failure | 500 | `{ "error": "internal", "message": "string" }` |

All error bodies share one shape:
`{ "error": "machine_readable_code", "message": "human sentence" }`.
