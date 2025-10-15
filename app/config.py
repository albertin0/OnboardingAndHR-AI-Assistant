from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
VECTOR_COLLECTION = os.getenv("VECTOR_COLLECTION", "company_policy")

# Embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "3"))

# JWT / Auth
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret_for_prod")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# Groq (stub placeholder)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", api_key)

# DB
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'policy_mcp.db'}")
