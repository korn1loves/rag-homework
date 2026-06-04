"""Retrieval: load TF-IDF index and search top-k chunks by cosine similarity."""

import pickle
from pathlib import Path

import scipy.sparse
from sklearn.metrics.pairwise import cosine_similarity

from app.chunker import load_documents
from app.config import INDEX_CHUNKS_JSONL, MATRIX_NPZ, TOP_K, VECTORIZER_PKL


class Retriever:
    """TF-IDF retriever for indexed chunks."""

    def __init__(
        self,
        vectorizer_path: Path = VECTORIZER_PKL,
        matrix_path: Path = MATRIX_NPZ,
        chunks_path: Path = INDEX_CHUNKS_JSONL,
    ) -> None:
        self.vectorizer = self._load_vectorizer(vectorizer_path)
        self.matrix = self._load_matrix(matrix_path)
        self.chunks = load_documents(chunks_path)

        if self.matrix.shape[0] != len(self.chunks):
            raise ValueError("Matrix rows count does not match chunks count")

    @staticmethod
    def _load_vectorizer(path: Path):
        if not path.exists():
            raise FileNotFoundError(
                f"Index file not found: {path}. "
                "Run: uv run python scripts/build_index.py"
            )

        with path.open("rb") as f:
            return pickle.load(f)

    @staticmethod
    def _load_matrix(path: Path) -> scipy.sparse.csr_matrix:
        if not path.exists():
            raise FileNotFoundError(
                f"Index file not found: {path}. "
                "Run: uv run python scripts/build_index.py"
            )

        return scipy.sparse.load_npz(path)

    def search(self, query: str, k: int = TOP_K) -> list[dict]:
        """Return top-k chunks for the query."""
        if not query.strip():
            return []

        if k <= 0:
            return []

        k = min(k, len(self.chunks))

        query_vector = self.vectorizer.transform([query.strip()])
        scores = cosine_similarity(query_vector, self.matrix).flatten()

        top_indices = scores.argsort()[::-1][:k]

        results: list[dict] = []

        for idx in top_indices:
            chunk = self.chunks[int(idx)]

            results.append(
                {
                    "text": chunk["text"],
                    "doc_id": chunk["doc_id"],
                    "title": chunk.get("title", ""),
                    "source": chunk.get("source", ""),
                    "questions": chunk.get("questions", []),
                    "score": float(scores[int(idx)]),
                }
            )

        return results