import ollama
from typing import List, Dict
from embeddings.vector_store import search
from embeddings.embedder import embed_query
from config.settings import OLLAMA_MODEL, TOP_K_RESULTS


def get_answer(question: str, top_k: int = TOP_K_RESULTS) -> Dict:
    """
    Full RAG pipeline:
    1. Embed the question
    2. Search FAISS for relevant chunks
    3. Build prompt with context
    4. Ask Ollama
    5. Return answer + sources
    """

    # Step 1 — Embed the question
    query_embedding = embed_query(question)

    # Step 2 — Find relevant chunks
    relevant_chunks = search(query_embedding, top_k=top_k)

    if not relevant_chunks:
        return {
            "answer": "I could not find relevant code for your question.",
            "sources": []
        }

    # Step 3 — Build context from chunks
    context = ""
    for i, chunk in enumerate(relevant_chunks):
        context += f"\n--- File: {chunk['relative_path']} ---\n"
        context += chunk["chunk_text"]
        context += "\n"

    # Step 4 — Build the prompt
    prompt = f"""You are an expert software engineer helping a developer understand a codebase.

Use the following code snippets to answer the question.
Be clear, concise and beginner-friendly.
Always mention which file the answer comes from.

CODE CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

    # Step 5 — Ask Ollama
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["message"]["content"]
    except Exception as e:
        answer = f"Error connecting to Ollama: {e}\nMake sure Ollama is running with: ollama serve"

    # Step 6 — Return answer + sources
    sources = list(set(chunk["relative_path"] for chunk in relevant_chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(relevant_chunks)
    }


if __name__ == "__main__":
    question = "How does Flask handle routing?"
    print(f"\n❓ Question: {question}\n")
    result = get_answer(question)
    print(f"✅ Answer:\n{result['answer']}")
    print(f"\n📁 Sources: {result['sources']}")