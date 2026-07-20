"""FAISS vector store.

Contract
--------
    add(ids: list[str], vectors: list[list[float]]) -> None
    search(vector: list[float], k: int) -> list[tuple[str, float]]

- add() indexes profile vectors keyed by researcher id.
- search() returns the k nearest researcher ids with similarity scores,
  best first.
- Index files (*.faiss, *.index) are build artifacts: never committed,
  always rebuildable from ingested data.
"""


def add(ids: list[str], vectors: list[list[float]]) -> None:
    """Index vectors under the given researcher ids. Stub."""
    raise NotImplementedError("stub: FAISS indexing not implemented yet")


def search(vector: list[float], k: int) -> list[tuple[str, float]]:
    """Return the k nearest researcher ids with scores. Stub."""
    raise NotImplementedError("stub: FAISS search not implemented yet")
