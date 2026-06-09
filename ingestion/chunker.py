from typing import List, Dict
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_file_record(file_record: Dict) -> List[Dict]:
    """
    Splits a file's content into smaller overlapping chunks.
    Each chunk becomes one searchable unit in FAISS.
    """
    content = file_record["content"]
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(content):
        end = start + CHUNK_SIZE
        chunk_text = content[start:end]

        chunks.append({
            "chunk_text": chunk_text,
            "chunk_index": chunk_index,
            "file_path": file_record["file_path"],
            "relative_path": file_record["relative_path"],
            "repo_name": file_record["repo_name"],
            "language": file_record["language"],
            "extension": file_record["extension"],
        })

        start += CHUNK_SIZE - CHUNK_OVERLAP
        chunk_index += 1

    return chunks


def chunk_all_files(file_records: List[Dict]) -> List[Dict]:
    """
    Chunks every file record.
    Returns a flat list of all chunks across all files.
    """
    all_chunks = []
    for record in file_records:
        all_chunks.extend(chunk_file_record(record))
    return all_chunks


if __name__ == "__main__":
    from ingestion.repo_reader import load_repository
    from ingestion.code_parser import parse_all_files

    records = load_repository("https://github.com/pallets/flask")
    parsed = parse_all_files(records)
    chunks = chunk_all_files(parsed)

    print(f"\n✅ Total chunks created: {len(chunks)}")
    print(f"\n🔎 Sample Chunk:")
    print(f"  File    : {chunks[0]['relative_path']}")
    print(f"  Length  : {len(chunks[0]['chunk_text'])} characters")
    print(f"  Preview : {chunks[0]['chunk_text'][:150]}...")