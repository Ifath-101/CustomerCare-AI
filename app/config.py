import os

GEMINI_API_KEY = "AIzaSyBxM_vBuxNDKRluKnDEpg0MLdlng6_pjpA"

DATABASE_URL = "postgresql://postgres:ifath%40456@localhost:5432/email_replier_db"

# Embedding / FAISS files
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "data/faiss_index.index"
ID_MAP_PATH = "data/faiss_id_map.json"

# Retrieval settings
TOP_K = 5
SIMILARITY_THRESHOLD = 0.30  # 0-1, tune later