import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv() # Fallback to current working directory .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2").strip()

DB_PATH = BASE_DIR / "data" / "candidate.db"
CHROMA_DIR = BASE_DIR / "data" / "chroma_store"
DOCS_DIR = BASE_DIR / "data" / "docs"

def has_gemini_key() -> bool:
    return bool(GEMINI_API_KEY and not GEMINI_API_KEY.startswith("your_"))

def has_hf_token() -> bool:
    return bool(HF_TOKEN and not HF_TOKEN.startswith("your_"))
