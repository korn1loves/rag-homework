"""Check retrieval for iteration 5."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.retriever import Retriever


def print_hit(i: int, hit: dict) -> None:
    """Print one retrieval result."""
    preview = hit["text"][:180].replace("\n", " ")

    print(f"  [{i}] doc_id={hit['doc_id']}, score={hit['score']:.4f}")
    print(f"      title={hit['title']}")
    print(f"      source={hit['source']}")
    print(f"      text={preview}...")


def main() -> None:
    print("=== Retrieval check ===\n")

    retriever = Retriever()
    print("OK: index loaded\n")

    queries = [
        (
            "Beyonce late 1990s",
            "Relevant SQuAD query. Expected: score > 0.",
        ),
        (
            "Destiny's Child Beyonce",
            "Relevant SQuAD query. Expected: score > 0.",
        ),
        (
            "What is the price of the newest iPhone?",
            "Negative query. Expected: low score or unrelated chunks.",
        ),
    ]

    for query, expectation in queries:
        print(f"Query: {query}")
        print(f"Expectation: {expectation}")

        results = retriever.search(query, k=3)

        print(f"Results: {len(results)}")
        for i, hit in enumerate(results, 1):
            print_hit(i, hit)

        print()

    print("If you see results with doc_id / score / title / source / text, iteration 5 works.")


if __name__ == "__main__":
    main()