"""Text embedding.

Contract
--------
    embed(texts: list[str]) -> list[list[float]]

- Input: a list of strings (student interest statements, profile summaries).
- Output: one fixed-dimension float vector per input string, same order.
- The embedding model is pinned per deployment; the dimension must match
  what the vector store was built with (see vector_store.py).
"""


def embed(texts: list[str]) -> list[list[float]]:
    """Embed texts into fixed-dimension vectors. Stub."""
    raise NotImplementedError("stub: embedding not implemented yet")
