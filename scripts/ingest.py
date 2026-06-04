"""Ingestion: datasets.json -> documents.jsonl."""

import json
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import DOCUMENTS_JSONL, RAW_DATASETS


def clean_text(text: str) -> str:
    """Normalize spaces and line breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def load_datasets(path: Path) -> list[dict]:
    """Load datasets from data/raw/datasets.json."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["datasets"]


def ingest_item(item: dict, source_file: str) -> dict:
    """Convert one raw dataset item to one normalized document."""
    return {
        "doc_id": str(item["id"]),
        "title": item["title"].strip(),
        "text": clean_text(item["text"]),
        "source": item.get("source", ""),
        "questions": item.get("questions", []),
        "source_file": source_file,
    }


def write_documents(documents: list[dict], path: Path) -> None:
    """Write documents to JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def run(
    input_path: Path = RAW_DATASETS,
    output_path: Path = DOCUMENTS_JSONL,
) -> int:
    """Run ingestion pipeline."""
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    source_file = str(input_path.relative_to(ROOT_DIR))
    datasets = load_datasets(input_path)
    documents = [ingest_item(item, source_file) for item in datasets]

    write_documents(documents, output_path)
    return len(documents)


def main() -> None:
    count = run()
    print(f"Wrote {count} documents to {DOCUMENTS_JSONL}")


if __name__ == "__main__":
    main()