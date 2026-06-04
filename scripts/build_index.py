"""Build TF-IDF index: ingest + chunk + fit + save."""

import pickle
import shutil
import sys
from pathlib import Path

import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from app.chunker import load_documents, run as chunk_run
from app.config import (
    CHUNKS_JSONL,
    INDEX_CHUNKS_JSONL,
    INDEX_DIR,
    MATRIX_NPZ,
    VECTORIZER_PKL,
)
from ingest import run as ingest_run


def build_tfidf(texts: list[str]) -> tuple[TfidfVectorizer, scipy.sparse.csr_matrix]:
    """Fit TF-IDF vectorizer on chunk texts."""
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


def save_index(
    vectorizer: TfidfVectorizer,
    matrix: scipy.sparse.csr_matrix,
    chunks_path: Path = CHUNKS_JSONL,
) -> int:
    """Save vectorizer, matrix and indexed chunks."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    with VECTORIZER_PKL.open("wb") as f:
        pickle.dump(vectorizer, f)

    scipy.sparse.save_npz(MATRIX_NPZ, matrix)
    shutil.copy2(chunks_path, INDEX_CHUNKS_JSONL)

    return matrix.shape[0]


def run() -> int:
    """Run full indexing pipeline."""
    doc_count = ingest_run()
    chunk_count = chunk_run()

    chunks = load_documents(CHUNKS_JSONL)
    texts = [chunk["text"] for chunk in chunks]

    if not texts:
        raise ValueError("No chunks found for indexing")

    vectorizer, matrix = build_tfidf(texts)
    save_index(vectorizer, matrix)

    print(f"Documents: {doc_count}")
    print(f"Chunks: {chunk_count}")
    print(f"Matrix shape: {matrix.shape}")
    print(f"Index saved to: {INDEX_DIR}")

    return chunk_count


def main() -> None:
    run()


if __name__ == "__main__":
    main()