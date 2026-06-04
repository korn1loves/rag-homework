"""Streamlit UI: question -> fragments -> answer -> sources."""

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import INDEX_CHUNKS_JSONL, MATRIX_NPZ, TOP_K, VECTORIZER_PKL
from app.generator import ask
from app.prompts import MIN_SCORE
from app.retriever import Retriever


DEMO_QUESTIONS = [
    "When did Beyonce start becoming popular?",
    "What areas did Beyonce compete in when she was growing up?",
    "In what city and state did Beyonce grow up?",
    "What is the price of the newest iPhone?",
]


def index_exists() -> bool:
    """Check that all index files exist."""
    return all(
        path.exists()
        for path in (VECTORIZER_PKL, MATRIX_NPZ, INDEX_CHUNKS_JSONL)
    )


@st.cache_resource
def load_retriever() -> Retriever:
    """Load retriever once and cache it in Streamlit."""
    return Retriever()


def render_chunk(i: int, source: dict, expanded: bool = True) -> None:
    """Render one source chunk."""
    label = (
        f"[{i}] doc_id={source['doc_id']} · "
        f"score={source['score']:.4f} · "
        f"title={source.get('title', '')}"
    )

    with st.expander(label, expanded=expanded):
        st.markdown(f"**Title:** {source.get('title', '')}")
        st.caption(f"Source: {source.get('source', '')}")
        st.text(source["text"])


def render_fragments(sources: list[dict]) -> None:
    """Render retrieved top-k fragments."""
    st.subheader("Retrieved fragments")

    if not sources:
        st.info("No fragments found.")
        return

    for i, source in enumerate(sources, 1):
        render_chunk(
            i,
            source,
            expanded=source["score"] >= MIN_SCORE,
        )


def render_sources(sources: list[dict]) -> None:
    """Render sources section."""
    st.subheader("Sources")

    if not sources:
        st.info("No sources.")
        return

    for i, source in enumerate(sources, 1):
        render_chunk(i, source, expanded=False)


def main() -> None:
    """Run Streamlit app."""
    st.set_page_config(page_title="SQuAD RAG Tutorial", layout="wide")

    st.title("SQuAD RAG Tutorial")
    st.caption("Educational RAG: SQuAD 2.0 + TF-IDF retrieval + demo answer with sources")

    if not index_exists():
        st.error(
            "Index is not built yet. Run this command first:\n\n"
            "`uv run python scripts/build_index.py`"
        )
        st.stop()

    st.sidebar.header("Demo questions")

    for question in DEMO_QUESTIONS:
        if st.sidebar.button(question, use_container_width=True):
            st.session_state["question"] = question

    question = st.text_input("Your question", key="question")

    top_k = st.sidebar.slider(
        "Top-k fragments",
        min_value=1,
        max_value=10,
        value=TOP_K,
    )

    if st.button("Ask", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
            st.stop()

        with st.spinner("Searching..."):
            result = ask(
                question.strip(),
                k=top_k,
                retriever=load_retriever(),
            )

        render_fragments(result["sources"])

        st.subheader("Answer")
        st.text(result["answer"])

        render_sources(result["sources"])


if __name__ == "__main__":
    main()