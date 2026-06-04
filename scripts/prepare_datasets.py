"""Prepare SQuAD 2.0 data for the educational RAG project.

Output:
    data/raw/datasets.json
"""

import json
from pathlib import Path
from urllib.request import urlopen

ROOT_DIR = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT_DIR / "data" / "raw" / "datasets.json"

SQUAD_URL = "https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v2.0.json"
LIMIT = 1200


def normalize_text(text: str) -> str:
    """Normalize spaces in a text fragment."""
    return " ".join(text.split()).strip()


def download_squad() -> dict:
    """Download SQuAD 2.0 train JSON."""
    with urlopen(SQUAD_URL, timeout=120) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def extract_datasets(raw_data: dict, limit: int = LIMIT) -> list[dict]:
    """Convert SQuAD paragraphs to RAG documents."""
    datasets: list[dict] = []
    seen_contexts: set[str] = set()

    for article in raw_data["data"]:
        title = article.get("title", "").strip()

        for paragraph in article.get("paragraphs", []):
            context = normalize_text(paragraph.get("context", ""))

            if not context or context in seen_contexts:
                continue

            questions = []
            for qa in paragraph.get("qas", [])[:5]:
                answers = qa.get("answers", [])
                is_impossible = bool(qa.get("is_impossible", False))

                if is_impossible or not answers:
                    answer = ""
                else:
                    answer = answers[0].get("text", "")

                questions.append(
                    {
                        "question": qa.get("question", "").strip(),
                        "answer": answer,
                        "is_impossible": is_impossible,
                    }
                )

            if not questions:
                continue

            doc_id = f"squad_{len(datasets):05d}"

            datasets.append(
                {
                    "id": doc_id,
                    "title": title,
                    "text": context,
                    "source": "SQuAD 2.0 / Wikipedia",
                    "questions": questions,
                }
            )

            seen_contexts.add(context)

            if len(datasets) >= limit:
                return datasets

    return datasets


def main() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    raw_data = download_squad()
    datasets = extract_datasets(raw_data)

    if len(datasets) < 1000:
        raise ValueError(f"Expected at least 1000 records, got {len(datasets)}")

    OUT_JSON.write_text(
        json.dumps({"datasets": datasets}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {len(datasets)} records to {OUT_JSON}")


if __name__ == "__main__":
    main()