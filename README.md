markdown<div align="center">

# 🧠 Codebase Knowledge AI

### Chat with any GitHub repository in plain English

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-green?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-orange?style=for-the-badge)

</div>

---
## 🌐 Live Demo

👉 **[Try it live here](https://codebase-knowledge-ai-satish.streamlit.app/)**

> No installation needed. Just open and use!
---
---

## 🚀 What Is This?

**Codebase Knowledge AI** is an AI-powered developer tool that reads any GitHub repository and lets you ask questions about it in plain English.

No more spending weeks reading code. Just ask:

- 💬 *"How does authentication work?"*
- 💬 *"Where is payment processing handled?"*
- 💬 *"What does the Flask routing system do?"*

And get instant, accurate answers with source file references.

---

## ⚙️ How It Works

| Step | Component | Action |
|------|-----------|--------|
| 1 | 📥 Repository Reader | Clones repo, reads all files |
| 2 | 🔬 Code Parser | Extracts functions, classes, imports (AST) |
| 3 | ✂️ Chunker | Splits files into searchable chunks |
| 4 | 🧠 Embedding Engine | Converts chunks to vectors |
| 5 | 🗄️ FAISS Vector Store | Stores and searches vectors by meaning |
| 6 | 💬 RAG Engine | Retrieves context + asks Ollama |
| 7 | ✅ Answer | Plain English response with sources |
---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| 🐍 Language | Python 3.8+ | Core language |
| 🎨 UI | Streamlit | Web chat interface |
| 📦 Repo Reading | GitPython | Clone & walk repositories |
| 🔬 Code Parsing | Python AST | Extract code structure |
| 🧠 Embeddings | sentence-transformers | Convert text to vectors |
| 🗄️ Vector DB | FAISS | Semantic similarity search |
| 🤖 LLM | Ollama (Llama 3.2) | Generate answers locally |

> 💡 **100% Free & Local** — No paid APIs. Everything runs on your machine.

---

## 📁 Project Structure

| Folder | File | Purpose |
|--------|------|---------|
| `app/` | `main.py` | Streamlit chat interface |
| `ingestion/` | `repo_reader.py` | Clone & read GitHub repos |
| `ingestion/` | `code_parser.py` | AST code structure extraction |
| `ingestion/` | `chunker.py` | Split files into chunks |
| `embeddings/` | `embedder.py` | Generate vector embeddings |
| `embeddings/` | `vector_store.py` | FAISS index management |
| `rag/` | `answer_engine.py` | RAG pipeline + Ollama |
| `config/` | `settings.py` | Central configuration |

---

## 🏃 Quick Start

### 1. Clone this repo
```bash
git clone https://github.com/satish-5140/codebase-knowledge-ai.git
cd codebase-knowledge-ai
```

### 2. Create virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Ollama + pull model
Download from 👉 https://ollama.com/download
```bash
ollama pull llama3.2
```

### 5. Run the app
```bash
streamlit run app/main.py
```

### 6. Open browser
http://localhost:8501

---

## 💡 Example Questions

Once a repo is loaded, try asking:

| Question | What It Finds |
|----------|--------------|
| How does routing work? | Route decorators, URL rules |
| Where is authentication handled? | Auth middleware, login functions |
| What does the main app class do? | Core application logic |
| How are requests processed? | Request lifecycle code |

---

## 🧠 Key Concepts Used

| Concept | What It Means |
|---------|--------------|
| **RAG** | Retrieve relevant code → Give it to LLM as context → Get accurate answer |
| **Embeddings** | Converting text into numbers that capture meaning |
| **Vector Search** | Finding similar content mathematically, not by keyword |
| **AST Parsing** | Reading code structure (functions, classes) programmatically |
---

## ✨ Features

- 🔍 **Semantic Search** — Finds code by meaning, not just keywords
- 🤖 **AI Answers** — Plain English explanations powered by Groq LLM
- 🔗 **Dependency Mapping** — See which files connect to which
- 🕸️ **Visual Code Graph** — Interactive graph of entire codebase
- ⚡ **Fast** — Groq API gives lightning fast responses
- 🆓 **100% Free** — No paid APIs, free hosting on Streamlit Cloud

## 👨‍💻 Built By

**Satish** — CS Engineering Graduate, KLE Institute of Technology

[![GitHub](https://img.shields.io/badge/GitHub-satish--5140-black?style=flat&logo=github)](https://github.com/satish-5140)
[![Live Demo](https://img.shields.io/badge/Live-Demo-red?style=flat&logo=streamlit)](https://codebase-knowledge-ai-satish.streamlit.app/)

---

<div align="center">
⭐ Star this repo if you found it useful!
</div>
---
