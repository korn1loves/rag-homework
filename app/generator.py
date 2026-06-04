"""Demo answer: retrieved chunks -> answer + sources without external LLM."""

import re
from difflib import SequenceMatcher

from app.config import TOP_K
from app.prompts import MIN_SCORE, REFUSAL_EMPTY_QUESTION, REFUSAL_NO_CONTEXT
from app.retriever import Retriever


STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
    "did",
    "do",
    "does",
    "in",
    "on",
    "of",
    "to",
    "for",
    "and",
    "or",
    "with",
    "by",
}


def tokenize(text: str) -> set[str]:
    """Tokenize text and remove common stopwords."""
    tokens = set(re.findall(r"[a-zA-Z0-9']+", text.lower()))
    return {token for token in tokens if token not in STOPWORDS}


def question_similarity(user_question: str, stored_question: str) -> float:
    """Calculate strict similarity between two questions."""
    user_tokens = tokenize(user_question)
    stored_tokens = tokenize(stored_question)

    if not user_tokens or not stored_tokens:
        return 0.0

    jaccard = len(user_tokens & stored_tokens) / len(user_tokens | stored_tokens)
    sequence = SequenceMatcher(
        None,
        user_question.lower().strip(),
        stored_question.lower().strip(),
    ).ratio()

    return max(jaccard, sequence)


def find_known_answer(question: str, hits: list[dict]) -> str | None:
    """Find an answer only when the user question is very close to SQuAD metadata."""
    best_answer = None
    best_similarity = 0.0

    for hit in hits:
        if hit["score"] < MIN_SCORE:
            continue

        for qa in hit.get("questions", []):
            stored_question = qa.get("question", "")
            answer = qa.get("answer", "")
            is_impossible = qa.get("is_impossible", False)

            if is_impossible or not answer:
                continue

            similarity = question_similarity(question, stored_question)

            if similarity > best_similarity:
                best_similarity = similarity
                best_answer = answer

    if best_similarity >= 0.70:
        return best_answer

    return None


def build_answer(question: str, hits: list[dict]) -> str:
    """Build an answer only from relevant retrieved chunks."""
    relevant = [hit for hit in hits if hit["score"] >= MIN_SCORE]

    if not relevant:
        return REFUSAL_NO_CONTEXT

    known_answer = find_known_answer(question, relevant)

    if not known_answer:
        return REFUSAL_NO_CONTEXT

    first = relevant[0]
    return (
        f"Answer: {known_answer}\n\n"
        f"Source: {first.get('title', '')} "
        f"(doc_id={first['doc_id']}, score={first['score']:.4f})"
    )


def format_sources(hits: list[dict]) -> list[dict]:
    """Return sources for UI and console output."""
    return [
        {
            "doc_id": hit["doc_id"],
            "title": hit.get("title", ""),
            "source": hit.get("source", ""),
            "text": hit["text"],
            "score": hit["score"],
        }
        for hit in hits
    ]


def ask(
    question: str,
    k: int = TOP_K,
    retriever: Retriever | None = None,
) -> dict:
    """User question -> demo answer and sources."""
    if not question.strip():
        return {"answer": REFUSAL_EMPTY_QUESTION, "sources": []}

    r = retriever or Retriever()
    hits = r.search(question.strip(), k=k)

    return {
        "answer": build_answer(question.strip(), hits),
        "sources": format_sources(hits),
    }