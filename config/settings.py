import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────
# BASE PATHS
# ─────────────────────────────────────────

# Root of the entire project
BASE_DIR = Path(__file__).resolve().parent.parent

# Where cloned repositories will be stored
REPOS_DIR = BASE_DIR / "data" / "repos"

# Where FAISS vector indexes will be saved
FAISS_INDEX_DIR = BASE_DIR / "data" / "faiss_index"

# Where SQLite database will be stored
DB_DIR = BASE_DIR / "data" / "db"
DB_PATH = DB_DIR / "codebase.db"

# ─────────────────────────────────────────
# REPOSITORY SETTINGS
# ─────────────────────────────────────────

# File types we want to read and analyze
SUPPORTED_EXTENSIONS = [
    ".py",    # Python
    ".js",    # JavaScript
    ".ts",    # TypeScript
    ".java",  # Java
    ".cpp",   # C++
    ".c",     # C
    ".go",    # Go
    ".rs",    # Rust
    ".rb",    # Ruby
    ".md",    # Markdown (documentation)
    ".txt",   # Text files
    ".yaml",  # Config files
    ".yml",   # Config files
    ".json",  # JSON configs
    ".toml",  # Config files
    ".env.example",  # Example env files (not real .env)
]

# Folders we should completely ignore
IGNORED_DIRS = [
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    "env",
    ".venv",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".pytest_cache",
    "migrations",   # DB migrations are usually auto-generated
    ".idea",
    ".vscode",
]

# Maximum file size to read (in bytes) — skip huge files
MAX_FILE_SIZE_BYTES = 500_000  # 500 KB

# ─────────────────────────────────────────
# EMBEDDING SETTINGS
# ─────────────────────────────────────────

# The sentence-transformer model we'll use for embeddings
# This is a small, fast, high-quality model — great for code
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# How many characters per chunk when splitting files
CHUNK_SIZE = 1500

# How many characters overlap between chunks
# (So context isn't lost at chunk boundaries)
CHUNK_OVERLAP = 200

# ─────────────────────────────────────────
# OLLAMA SETTINGS
# ─────────────────────────────────────────

# The LLM model running in Ollama
OLLAMA_MODEL = "llama3.2"

# Ollama runs locally on this address
OLLAMA_BASE_URL = "http://localhost:11434"

# How many chunks to retrieve from FAISS per query
TOP_K_RESULTS = 5

# ─────────────────────────────────────────
# CREATE DIRECTORIES IF THEY DON'T EXIST
# ─────────────────────────────────────────

def create_project_directories():
    """Creates all required data directories on startup."""
    dirs = [REPOS_DIR, FAISS_INDEX_DIR, DB_DIR]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

# Auto-create directories when this file is imported
create_project_directories()

# ─────────────────────────────────────────
# GROQ SETTINGS
# ─────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"