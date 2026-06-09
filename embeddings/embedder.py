from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
from tqdm import tqdm
from config.settings import EMBEDDING_MODEL


# Load model once — reused for all embeddings
print(f"🧠 Loading embedding model: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)
print(f"✅ Model loaded.")


def embed_chunks(chunks: List[Dict], batch_size: int = 64) -> List[Dict]:
    """
    Takes all chunks and adds an 'embedding' field to each.
    Embedding is a list of numbers representing the meaning of the text.
    """
    texts = [chunk["chunk_text"] for chunk in chunks]

    print(f"\n⚙️  Generating embeddings for {len(texts)} chunks...")

    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="🔢 Embedding batches"):
        batch = texts[i: i + batch_size]
        batch_embeddings = model.encode(batch, show_progress_bar=False)
        all_embeddings.extend(batch_embeddings)

    # Add embedding to each chunk
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = all_embeddings[i]

    print(f"✅ Embeddings generated for {len(chunks)} chunks.")
    return chunks


def embed_query(query: str) -> np.ndarray:
    """
    Converts a user's question into an embedding vector.
    Used at search time to find similar chunks.
    """
    return model.encode(query)


if __name__ == "__main__":
    from ingestion.repo_reader import load_repository
    from ingestion.code_parser import parse_all_files
    from ingestion.chunker import chunk_all_files

    records = load_repository("https://github.com/pallets/flask")
    parsed = parse_all_files(records)
    chunks = chunk_all_files(parsed)
    embedded = embed_chunks(chunks)

    print(f"\n🔎 Sample Embedding:")
    print(f"  Chunk   : {embedded[0]['relative_path']}")
    print(f"  Vector  : {embedded[0]['embedding'][:5]}...")
    print(f"  Shape   : {embedded[0]['embedding'].shape}")