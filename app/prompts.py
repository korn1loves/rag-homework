"""Rules and constants for demo answer generation."""

SYSTEM_RULES = """
Answer only using the retrieved source fragments.
Do not invent facts, dates, names, numbers, or sources.
If the retrieved fragments are not relevant, refuse to answer.
""".strip()

REFUSAL_NO_CONTEXT = (
    "I do not have enough information in the provided sources to answer this question."
)

REFUSAL_EMPTY_QUESTION = "Please enter a question."

# Minimal score to treat a TF-IDF chunk as relevant.
MIN_SCORE = 0.05