"""Chunking: documents.jsonl -> chunks.jsonl."""

import json
from pathlib import Path

from app.config import CHUNK_MAX_CHARS, CHUNK_OVERLAP, CHUNKS_JSONL, DOCUMENTS_JSONL


def split_paragraphs(text: str) -> list[str]:
    """Split text into non-empty paragraphs."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def split_long_text(text: str, max_chars: int) -> list[str]:
    """Split a long paragraph into fixed-size parts."""
    if len(text) <= max_chars:
        return [text]

    parts: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))
        parts.append(text[start:end])
        start = end

    return parts


def apply_overlap(chunks: list[str], overlap: int, max_chars: int) -> list[str]:
    """Add overlap from the previous chunk to the next chunk."""
    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    result = [chunks[0]]

    for i in range(1, len(chunks)):
        prefix = chunks[i - 1][-overlap:]
        combined = prefix + chunks[i]

        if len(combined) > max_chars:
            combined = combined[:max_chars]

        result.append(combined)

    return result


def chunk_text(
    text: str,
    max_chars: int = CHUNK_MAX_CHARS,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into chunks by paragraphs with max size and overlap."""
    if not text.strip():
        return []

    raw_chunks: list[str] = []
    current_parts: list[str] = []

    def flush() -> None:
        if current_parts:
            raw_chunks.append("\n\n".join(current_parts))
            current_parts.clear()

    for paragraph in split_paragraphs(text):
        pieces = split_long_text(paragraph, max_chars)

        for piece in pieces:
            candidate_parts = current_parts + [piece]
            candidate = "\n\n".join(candidate_parts)

            if len(candidate) <= max_chars:
                current_parts = candidate_parts
            else:
                flush()
                current_parts = [piece]

    flush()

    return apply_overlap(raw_chunks, overlap, max_chars)


def chunk_document(doc: dict) -> list[dict]:
    """Convert one document to chunks with metadata."""
    chunks: list[dict] = []

    for i, text in enumerate(chunk_text(doc["text"])):
        chunks.append(
            {
                "chunk_id": f"{doc['doc_id']}_{i}",
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "source": doc.get("source", ""),
                "questions": doc.get("questions", []),
                "text": text,
            }
        )

    return chunks


def load_documents(path: Path) -> list[dict]:
    """Load JSONL documents."""
    documents: list[dict] = []

    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                documents.append(json.loads(line))

    return documents


def write_chunks(chunks: list[dict], path: Path) -> None:
    """Write chunks to JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")


def run(
    input_path: Path = DOCUMENTS_JSONL,
    output_path: Path = CHUNKS_JSONL,
) -> int:
    """Run chunking for all documents."""
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    documents = load_documents(input_path)

    all_chunks: list[dict] = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))

    write_chunks(all_chunks, output_path)
    return len(all_chunks)


def main() -> None:
    count = run()
    print(f"Wrote {count} chunks to {CHUNKS_JSONL}")


if __name__ == "__main__":
    main()