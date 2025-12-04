# app/services/embedding_service.py
import os
import json
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm

from app.config import EMBEDDING_MODEL, FAISS_INDEX_PATH, ID_MAP_PATH

# ensure folder
Path("data").mkdir(parents=True, exist_ok=True)

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    # ensure float32 for faiss
    return embeddings.astype("float32")


def build_faiss_index(items: List[Tuple[int, str]], index_path: str = FAISS_INDEX_PATH, id_path: str = ID_MAP_PATH):
    """
    items: list of (product_id, combined_text)
    Builds and saves a FAISS index and a mapping file (list of ids in the same order).
    """
    texts = [t for (_id, t) in items]
    ids = [int(_id) for (_id, t) in items]

    emb = embed_texts(texts)  # numpy float32 shape (n, d)
    d = emb.shape[1]

    # L2 index with inner product converted to cosine by normalizing vectors
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(emb)

    index = faiss.IndexFlatIP(d)  # inner product on normalized vectors is cosine
    index.add(emb)

    # Save index and id map
    faiss.write_index(index, index_path)
    with open(id_path, "w", encoding="utf-8") as f:
        json.dump(ids, f)

    return index, ids


def load_faiss_index(index_path: str = FAISS_INDEX_PATH, id_path: str = ID_MAP_PATH):
    if not os.path.exists(index_path) or not os.path.exists(id_path):
        return None, None
    index = faiss.read_index(index_path)
    with open(id_path, "r", encoding="utf-8") as f:
        ids = json.load(f)
    return index, ids


def query_faiss(query: str, top_k: int = 5):
    """
    Returns list of (product_id, score) sorted by score desc.
    Score is cosine similarity in [0,1].
    """
    index, ids = load_faiss_index()
    if index is None:
        return []

    q_emb = embed_texts([query])  # shape (1, d)
    faiss.normalize_L2(q_emb)
    scores, idxs = index.search(q_emb, top_k)  # scores shape (1, k)
    scores = scores[0].tolist()
    idxs = idxs[0].tolist()

    results = []
    for score, idx in zip(scores, idxs):
        if idx < 0 or idx >= len(ids):
            continue
        pid = ids[idx]
        results.append((pid, float(score)))  # score in [-1,1] but since normalized, [0,1]
    return results
