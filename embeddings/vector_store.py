import faiss
import numpy as np
import pickle
import os
from typing import List, Dict
from config.settings import FAISS_INDEX_DIR, TOP_K_RESULTS


# Paths where FAISS index and chunks are saved
INDEX_PATH = FAISS_INDEX_DIR / "index.faiss"
CHUNKS_PATH = FAISS_INDEX_DIR / "chunks.pkl"


def build_and_save(chunks: List[Dict]):
    """
    Takes embedded chunks, builds a FAISS index, and saves it to disk.
    """
    print(f"\n🗄️  Building FAISS index...")

    # Extract embeddings as a numpy array
    embeddings = np.array([chunk["embedding"] for chunk in chunks]).astype("float32")

    # Get the dimension size (384 for our model)
    dimension = embeddings.shape[1]

    # Create FAISS index — L2 = finds closest vectors by distance
    index = faiss.IndexFlatL2(dimension)

    # Add all embeddings to the index
    index.add(embeddings)

    print(f"✅ FAISS index built with {index.ntotal} vectors.")

    # Save FAISS index to disk
    faiss.write_index(index, str(INDEX_PATH))
    print(f"💾 FAISS index saved to: {INDEX_PATH}")

    # Save chunks (without embeddings) to disk
    # We need chunks to retrieve the actual text later
    chunks_to_save = []
    for chunk in chunks:
        c = chunk.copy()
        del c["embedding"]  # Don't save embeddings twice
        chunks_to_save.append(c)

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks_to_save, f)

    print(f"💾 Chunks saved to: {CHUNKS_PATH}")


def load_index():
    """
    Loads saved FAISS index and chunks from disk.
    """
    if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        raise FileNotFoundError("FAISS index not found. Run ingestion first.")

    index = faiss.read_index(str(INDEX_PATH))

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    print(f"✅ Loaded FAISS index with {index.ntotal} vectors.")
    return index, chunks


def search(query_embedding: np.ndarray, top_k: int = TOP_K_RESULTS):
    """
    Searches FAISS for the most similar chunks to the query.
    Returns top_k most relevant chunks.
    """
    index, chunks = load_index()

    # FAISS needs float32 and 2D array shape
    query = np.array([query_embedding]).astype("float32")

    # Search — returns distances and indexes of closest vectors
    distances, indices = index.search(query, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            chunk = chunks[idx]
            chunk["score"] = float(distances[0][i])
            results.append(chunk)

    return results


if __name__ == "__main__":
    from ingestion.repo_reader import load_repository
    from ingestion.code_parser import parse_all_files
    from ingestion.chunker import chunk_all_files
    from embeddings.embedder import embed_chunks, embed_query

    # Full pipeline test
    records = load_repository("https://github.com/pallets/flask")
    parsed = parse_all_files(records)
    chunks = chunk_all_files(parsed)
    embedded = embed_chunks(chunks)

    # Build and save FAISS index
    build_and_save(embedded)

    # Test search
    print(f"\n🔍 Testing search...")
    query = "how does flask handle routing"
    query_vec = embed_query(query)
    results = search(query_vec)

    print(f"\n✅ Top {len(results)} results for: '{query}'")
    for i, r in enumerate(results):
        print(f"\n  Result {i+1}: {r['relative_path']}")
        print(f"  Score  : {r['score']:.4f}")
        print(f"  Preview: {r['chunk_text'][:150]}...")