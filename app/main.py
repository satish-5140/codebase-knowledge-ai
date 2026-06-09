import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.repo_reader import load_repository
from ingestion.code_parser import parse_all_files
from ingestion.chunker import chunk_all_files
from embeddings.embedder import embed_chunks
from embeddings.vector_store import build_and_save, INDEX_PATH
from rag.answer_engine import get_answer


# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────

st.set_page_config(
    page_title="Codebase Knowledge AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Codebase Knowledge AI")
st.caption("Chat with any GitHub repository in plain English")


# ─────────────────────────────────────────
# SIDEBAR — REPO LOADER
# ─────────────────────────────────────────

with st.sidebar:
    st.header("📂 Load Repository")

    github_url = st.text_input(
        "GitHub URL",
        placeholder="https://github.com/pallets/flask"
    )

    load_btn = st.button("🚀 Load & Index Repository", use_container_width=True)

    if load_btn and github_url:
        with st.spinner("Loading repository..."):
            try:
                # Full pipeline
                records = load_repository(github_url)
                st.success(f"✅ Loaded {len(records)} files")

                with st.spinner("Parsing code..."):
                    parsed = parse_all_files(records)

                with st.spinner("Creating chunks..."):
                    chunks = chunk_all_files(parsed)
                    st.success(f"✅ Created {len(chunks)} chunks")

                with st.spinner("Generating embeddings... (this takes 1-2 mins)"):
                    embedded = embed_chunks(chunks)

                with st.spinner("Building FAISS index..."):
                    build_and_save(embedded)
                    st.success("✅ Repository indexed successfully!")
                    st.session_state["repo_loaded"] = True
                    st.session_state["repo_name"] = github_url.split("/")[-1]

            except Exception as e:
                st.error(f"Error: {e}")

    # Show status
    if INDEX_PATH.exists():
        st.success("✅ Index ready — ask questions!")
    else:
        st.warning("⚠️ No index found. Load a repo first.")

    st.divider()
    st.markdown("**Model:** all-MiniLM-L6-v2")
    st.markdown("**LLM:** Ollama llama3.2")


# ─────────────────────────────────────────
# MAIN AREA — CHAT
# ─────────────────────────────────────────

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📁 Sources"):
                for source in message["sources"]:
                    st.code(source)

# Chat input
if prompt := st.chat_input("Ask anything about the codebase..."):

    if not INDEX_PATH.exists():
        st.error("Please load a repository first using the sidebar.")
    else:
        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = get_answer(prompt)

            st.markdown(result["answer"])

            with st.expander(f"📁 Sources ({len(result['sources'])} files)"):
                for source in result["sources"]:
                    st.code(source)

        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"]
        })