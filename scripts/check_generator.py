"""Check demo answer for iteration 6."""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.generator import ask


def show(label: str, question: str) -> None:
    """Print answer and sources for one question."""
    print(f"\n--- {label}: {question} ---")

    result = ask(question)

    print("Answer:")
    print(result["answer"])
    print()

    print(f"Sources: {len(result['sources'])}")
    for i, source in enumerate(result["sources"], 1):
        print(
            f"  [{i}] doc_id={source['doc_id']}, "
            f"score={source['score']:.4f}, "
            f"title={source['title']}"
        )


def main() -> None:
    show("Relevant", "When did Beyonce start becoming popular?")
    show("Relevant", "What areas did Beyonce compete in when she was growing up?")
    show("Negative", "What is the price of the newest iPhone?")
    show("Empty", "   ")


if __name__ == "__main__":
    main()