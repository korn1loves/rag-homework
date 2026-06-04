"""Tests for retrieval and demo answer."""

import json
import pickle
from pathlib import Path

import pytest
import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from app.generator import ask
from app.prompts import REFUSAL_NO_CONTEXT
from app.retriever import Retriever


@pytest.fixture
def mini_index(tmp_path: Path) -> dict[str, Path]:
    """Create a small isolated TF-IDF index for tests."""
    chunks = [
        {
            "chunk_id": "squad_00000_0",
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
            "text": (
                "Beyonce started becoming popular in the late 1990s "
                "as lead singer of Destiny's Child."
            ),
        },
        {
            "chunk_id": "squad_00001_0",
            "doc_id": "squad_00001",
            "title": "Python",
            "source": "SQuAD 2.0 / Wikipedia",
            "questions": [
                {
                    "question": "What kind of programming language is Python?",
                    "answer": "high-level programming language",
                    "is_impossible": False,
                }
            ],
            "text": "Python is a high-level programming language.",
        },
    ]

    chunks_path = tmp_path / "chunks.jsonl"

    with chunks_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    texts = [
        " ".join(
            [
                chunk["title"],
                " ".join(q["question"] for q in chunk["questions"]),
                chunk["text"],
            ]
        )
        for chunk in chunks
    ]

    vectorizer = TfidfVectorizer(
        strip_accents="unicode",
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
    )
    matrix = vectorizer.fit_transform(texts)

    vectorizer_path = tmp_path / "vectorizer.pkl"
    matrix_path = tmp_path / "matrix.npz"

    with vectorizer_path.open("wb") as f:
        pickle.dump(vectorizer, f)

    scipy.sparse.save_npz(matrix_path, matrix)

    return {
        "vectorizer_path": vectorizer_path,
        "matrix_path": matrix_path,
        "chunks_path": chunks_path,
    }


def test_search_returns_k_results(mini_index):
    retriever = Retriever(**mini_index)

    results = retriever.search("Beyonce late 1990s", k=2)

    assert len(results) == 2


def test_search_results_have_required_fields(mini_index):
    retriever = Retriever(**mini_index)

    results = retriever.search("Beyonce", k=1)

    assert results
    hit = results[0]

    assert "text" in hit
    assert "doc_id" in hit
    assert "title" in hit
    assert "source" in hit
    assert "questions" in hit
    assert "score" in hit
    assert isinstance(hit["score"], float)


def test_search_prefers_relevant_document(mini_index):
    retriever = Retriever(**mini_index)

    results = retriever.search("When did Beyonce start becoming popular?", k=1)

    assert results[0]["doc_id"] == "squad_00000"
    assert results[0]["score"] > 0


def test_search_empty_query_returns_empty_list(mini_index):
    retriever = Retriever(**mini_index)

    assert retriever.search("") == []
    assert retriever.search("   ") == []


def test_ask_returns_answer_and_sources(mini_index):
    retriever = Retriever(**mini_index)

    result = ask(
        "When did Beyonce start becoming popular?",
        retriever=retriever,
    )

    assert "in the late 1990s" in result["answer"]
    assert result["sources"]
    assert result["sources"][0]["doc_id"] == "squad_00000"


def test_ask_refuses_without_relevant_context(mini_index):
    retriever = Retriever(**mini_index)

    result = ask(
        "What is the price of the newest iPhone?",
        retriever=retriever,
    )

    assert result["answer"] == REFUSAL_NO_CONTEXT