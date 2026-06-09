import os
import git
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm

# Import our central config
from config.settings import (
    REPOS_DIR,
    SUPPORTED_EXTENSIONS,
    IGNORED_DIRS,
    MAX_FILE_SIZE_BYTES
)


# ─────────────────────────────────────────
# DATA STRUCTURE
# ─────────────────────────────────────────

def make_file_record(
    file_path: str,
    relative_path: str,
    content: str,
    extension: str,
    size_bytes: int,
    repo_name: str
) -> Dict:
    """
    Creates a standard dictionary representing one file.
    Every file in our system will be represented this way.
    """
    return {
        "file_path": file_path,          # Full path on disk
        "relative_path": relative_path,  # Path relative to repo root
        "content": content,              # Full file content as string
        "extension": extension,          # e.g. ".py", ".js"
        "size_bytes": size_bytes,        # File size
        "repo_name": repo_name,          # Which repo this came from
        "language": get_language(extension),  # Human-readable language name
    }


def get_language(extension: str) -> str:
    """Maps file extension to human-readable language name."""
    language_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".md": "Markdown",
        ".txt": "Text",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".json": "JSON",
        ".toml": "TOML",
    }
    return language_map.get(extension, "Unknown")


# ─────────────────────────────────────────
# REPO CLONING
# ─────────────────────────────────────────

def clone_or_update_repo(github_url: str) -> Path:
    """
    Clones a GitHub repo if not already present.
    If already cloned, pulls latest changes.

    Returns the local path where repo is stored.
    """

    # Extract repo name from URL
    # Example: "https://github.com/user/my-project.git"
    # → repo_name = "my-project"
    repo_name = github_url.rstrip("/").split("/")[-1].replace(".git", "")
    local_path = REPOS_DIR / repo_name

    if local_path.exists():
        print(f"📂 Repo already exists at: {local_path}")
        print(f"🔄 Pulling latest changes...")
        try:
            repo = git.Repo(local_path)
            repo.remotes.origin.pull()
            print(f"✅ Repo updated successfully.")
        except Exception as e:
            print(f"⚠️  Could not pull updates: {e}. Using existing version.")
    else:
        print(f"⬇️  Cloning repo: {github_url}")
        print(f"📁 Saving to: {local_path}")
        try:
            git.Repo.clone_from(github_url, local_path)
            print(f"✅ Repo cloned successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to clone repo: {e}")

    return local_path


# ─────────────────────────────────────────
# FILE WALKING
# ─────────────────────────────────────────

def should_ignore_path(path: Path) -> bool:
    """
    Returns True if this path should be skipped.
    Checks against our IGNORED_DIRS list.
    """
    for part in path.parts:
        if part in IGNORED_DIRS:
            return True
    return False


def get_all_files(repo_path: Path) -> List[Path]:
    """
    Walks through every folder in the repo.
    Returns a list of all files that:
    - Have a supported extension
    - Are not in an ignored directory
    - Are not too large
    """
    all_files = []

    # rglob("*") means: recursively find EVERYTHING
    for file_path in repo_path.rglob("*"):

        # Skip directories, we only want files
        if not file_path.is_file():
            continue

        # Skip if in an ignored folder (like node_modules)
        if should_ignore_path(file_path.relative_to(repo_path)):
            continue

        # Skip if extension not in our supported list
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # Skip if file is too large
        if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
            print(f"⚠️  Skipping large file: {file_path.name} "
                  f"({file_path.stat().st_size // 1000} KB)")
            continue

        all_files.append(file_path)

    return all_files


# ─────────────────────────────────────────
# FILE READING
# ─────────────────────────────────────────

def read_file_safely(file_path: Path) -> Optional[str]:
    """
    Reads a file and returns its content as a string.
    Handles encoding errors gracefully.
    Returns None if the file cannot be read.
    """
    # Try UTF-8 first (most common)
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        pass

    # Fallback to latin-1 (handles most other encodings)
    try:
        return file_path.read_text(encoding="latin-1")
    except Exception:
        pass

    # If both fail, skip the file
    print(f"⚠️  Could not read file: {file_path.name}. Skipping.")
    return None


# ─────────────────────────────────────────
# MAIN FUNCTION — THE ENTRY POINT
# ─────────────────────────────────────────

def load_repository(github_url: str) -> List[Dict]:
    """
    MAIN FUNCTION of this file.

    Given a GitHub URL:
    1. Clones or updates the repo
    2. Finds all valid files
    3. Reads each file
    4. Returns a list of file records

    Each record is a dictionary with:
    file_path, relative_path, content, extension,
    size_bytes, repo_name, language
    """

    print("\n" + "="*50)
    print("🚀 CODEBASE KNOWLEDGE AI — Repository Loader")
    print("="*50)

    # Step 1: Clone or update repo
    repo_path = clone_or_update_repo(github_url)
    repo_name = repo_path.name

    # Step 2: Find all valid files
    print(f"\n🔍 Scanning files in: {repo_path}")
    all_files = get_all_files(repo_path)
    print(f"📊 Found {len(all_files)} valid files to process.\n")

    # Step 3: Read each file and build records
    file_records = []

    for file_path in tqdm(all_files, desc="📖 Reading files"):
        content = read_file_safely(file_path)

        if content is None:
            continue

        # Build the relative path (path from repo root)
        relative_path = str(file_path.relative_to(repo_path))

        record = make_file_record(
            file_path=str(file_path),
            relative_path=relative_path,
            content=content,
            extension=file_path.suffix.lower(),
            size_bytes=file_path.stat().st_size,
            repo_name=repo_name,
        )
        file_records.append(record)

    # Step 4: Summary
    print(f"\n✅ Successfully loaded {len(file_records)} files.")
    print_summary(file_records)

    return file_records


# ─────────────────────────────────────────
# UTILITY — SUMMARY PRINTER
# ─────────────────────────────────────────

def print_summary(file_records: List[Dict]):
    """Prints a breakdown of files by language."""
    from collections import Counter

    language_counts = Counter(r["language"] for r in file_records)

    print("\n📋 Files by Language:")
    print("-" * 30)
    for language, count in language_counts.most_common():
        print(f"  {language:<20} {count} files")
    print("-" * 30)
    total_size = sum(r["size_bytes"] for r in file_records)
    print(f"  Total size: {total_size // 1000} KB")
    print()


# ─────────────────────────────────────────
# QUICK TEST — Run this file directly
# ─────────────────────────────────────────

if __name__ == "__main__":
    # Test with a small public repo
    TEST_URL = "https://github.com/pallets/flask"

    records = load_repository(TEST_URL)

    # Print first file as sample
    if records:
        sample = records[0]
        print("\n🔎 Sample File Record:")
        print(f"  Path     : {sample['relative_path']}")
        print(f"  Language : {sample['language']}")
        print(f"  Size     : {sample['size_bytes']} bytes")
        print(f"  Preview  : {sample['content'][:200]}...")