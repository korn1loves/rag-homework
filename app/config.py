"""Project configuration: paths and RAG parameters."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "index"

RAW_DATASETS = RAW_DIR / "datasets.json"

DOCUMENTS_JSONL = PROCESSED_DIR / "documents.jsonl"
CHUNKS_JSONL = PROCESSED_DIR / "chunks.jsonl"

VECTORIZER_PKL = INDEX_DIR / "vectorizer.pkl"
MATRIX_NPZ = INDEX_DIR / "matrix.npz"
INDEX_CHUNKS_JSONL = INDEX_DIR / "chunks.jsonl"

TOP_K = 3

CHUNK_MAX_CHARS = 900
CHUNK_OVERLAP = 120

MIN_SCORE = 0.05