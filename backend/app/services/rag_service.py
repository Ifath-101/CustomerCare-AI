# app/services/rag_service.py
from typing import List, Dict, Optional
from app.services.embedding_service import query_faiss
from app.config import TOP_K, SIMILARITY_THRESHOLD
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.product import Product

def retrieve_candidates(query: str, top_k: int = TOP_K):
    """
    Returns a list of candidate product dicts with similarity score.
    """
    from app.database import get_db
    # get ids and scores from faiss
    hits = query_faiss(query, top_k=top_k)
    if not hits:
        return []

    db = next(get_db())
    products = []
    for pid, score in hits:
        p = db.query(Product).filter(Product.id == pid).first()
        if p:
            products.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "stock": p.stock,
                "price": float(p.price),
                "score": score
            })
    return products


def choose_best_candidate(candidates: List[Dict]) -> Optional[Dict]:
    """
    Return the best candidate if its score >= threshold else None
    """
    if not candidates:
        return None
    # top is sorted by FAISS already
    best = candidates[0]
    if best["score"] >= SIMILARITY_THRESHOLD:
        return best
    return None
