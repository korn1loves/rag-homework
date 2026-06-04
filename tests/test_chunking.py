"""Tests for text chunking."""

import json

from app.chunker import chunk_document, chunk_text, run


def test_chunk_text_respects_max_size():
    text = "Paragraph one.\n\n" + "word " * 300
    chunks = chunk_text(text, max_chars=400, overlap=50)

    assert chunks
    assert all(len(chunk) <= 400 for chunk in chunks)


def test_chunk_text_splits_by_paragraphs():
    text = "First paragraph about Beyonce.\n\nSecond paragraph about music."
    chunks = chunk_text(text, max_chars=400, overlap=50)

    assert len(chunks) == 1
    assert "Beyonce" in chunks[0]
    assert "music" in chunks[0]


def test_chunk_text_overlap_between_chunks():
    paragraph_1 = "A" * 300
    paragraph_2 = "B" * 300
    text = f"{paragraph_1}\n\n{paragraph_2}"

    chunks = chunk_text(text, max_chars=400, overlap=50)

    assert len(chunks) >= 2
    assert chunks[1].startswith(chunks[0][-50:])


def test_chunk_document_has_metadata():
    doc = {
        "doc_id": "squad_00000",
        "title": "Beyoncé",
        "source": "SQuAD 2.0 / Wikipedia",
        "questions": [
            {
                "question": "When did Beyonce start becoming popular?",
                "answer": "in the late 1990s",
                "is_impossible": False,
            }
        ],
        "text": "Beyonce rose to fame in the late 1990s.",
    }

    chunks = chunk_document(doc)

    assert len(chunks) == 1
    assert chunks[0]["chunk_id"] == "squad_00000_0"
    assert chunks[0]["doc_id"] == "squad_00000"
    assert chunks[0]["title"] == "Beyoncé"
    assert chunks[0]["source"] == "SQuAD 2.0 / Wikipedia"
    assert "questions" in chunks[0]


def test_run_creates_chunks_jsonl(tmp_path):
    documents_path = tmp_path / "documents.jsonl"
    output_path = tmp_path / "chunks.jsonl"

    doc = {
        "doc_id": "squad_00000",
        "title": "Beyoncé",
        "source": "SQuAD 2.0 / Wikipedia",
        "questions": [],
        "text": "Beyonce rose to fame in the late 1990s.",
    }

    documents_path.write_text(
        json.dumps(doc, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    count = run(input_path=documents_path, output_path=output_path)

    assert count == 1
    assert output_path.exists()

    saved = json.loads(output_path.read_text(encoding="utf-8").strip())

    assert saved["doc_id"] == "squad_00000"
    assert saved["title"] == "Beyoncé"
    assert saved["source"] == "SQuAD 2.0 / Wikipedia"