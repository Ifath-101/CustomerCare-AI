# app/services/ai_product_service.py
import json
from typing import List, Dict, Optional
from app.services.rag_service import retrieve_candidates, choose_best_candidate
from app.config import GEMINI_API_KEY
import google.generativeai as genai

# configure genai (if present)
try:
    genai.configure(api_key=GEMINI_API_KEY)
    _HAS_GENAI = True
except Exception:
    _HAS_GENAI = False


def _extract_json_from_text(text: str) -> Optional[str]:
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return text[start:end]
    except ValueError:
        return None


def _safe_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        j = _extract_json_from_text(text)
        if j:
            try:
                return json.loads(j)
            except Exception:
                return None
        return None


def _build_candidates_text(cands: List[Dict]) -> str:
    lines = []
    for c in cands:
        desc = (c.get("description") or "").replace("\n", " ").strip()
        if len(desc) > 220:
            desc = desc[:217] + "..."
        lines.append(
            f"- id: {c['id']}, name: {c['name']}, desc: {desc}, price: {c.get('price')}, stock: {c.get('stock')}, score: {c.get('score'):.3f}"
        )
    return "\n".join(lines)


def analyze_email(email_body: str, products: List[Dict]):
    candidates = retrieve_candidates(email_body, top_k=5)
    print("DEBUG: RAG candidates:", candidates)

    def build_candidates_text(cands):
        lines = []
        for c in cands:
            desc = (c.get("description") or "").replace("\n", " ").strip()
            if len(desc) > 150:
                desc = desc[:147] + "..."
            lines.append(
                f"- id: {c['id']}, name: {c['name']}, desc: {desc}, price: Rs. {c.get('price')}, stock: {c.get('stock')}, score: {c.get('score'):.3f}"
            )
        return "\n".join(lines) if cands else "None"

    candidate_text = build_candidates_text(candidates)

    prompt = f"""
You are a helpful, professional customer support assistant.

Customer email:
----------------
{email_body}
----------------

Products retrieved from our database (with scores):
{candidate_text}

Instructions:
- Determine if the email is a product inquiry or a complaint (customer unhappy / issue / negative experience).
-If it is a complaint simply mark "is_complaint": true and "is_inquiry": false and do not do anything else
- If it isa product inquiry, select only relevant products from the list above and generate a human-like, professional email reply to the customer that:
    * Clearly lists only relevant products with name, price, stock, and description.
    * Uses friendly and natural tone.
    * Does not mention "auto-generated" or similar phrases.
    * Only include products that match the inquiry; ignore unrelated ones.
    * If no products match, politely inform the customer and suggest similar products.
- Return ONLY JSON exactly like this:

{{
  "is_inquiry": true/false,
  "is_complaint": true/false,
  "reason": "short explanation",
  "best_match_product_id": integer or null,
  "confidence": 0.0-1.0,
  "reply_text": "full email reply body"
}}
"""

    if _HAS_GENAI:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash") if hasattr(genai, "GenerativeModel") else None
            if model:
                resp = model.generate_content(prompt)
                raw = resp.text.strip()
                print("DEBUG: Gemini raw output:", raw[:1000])
                parsed = _safe_parse_json(raw)
                if parsed and isinstance(parsed, dict) and "is_inquiry" in parsed:
                    # Only consider confidence > 0.5
                    confidence = float(parsed.get("confidence") or 0.0)

                    # complaint passes through even low confidence
                    if parsed.get("is_complaint"):
                        return {
                            "is_inquiry": False,
                            "is_complaint": True,   # <<< ADDED
                            "reason": parsed.get("reason"),
                            "best_match_product_id": None,
                            "confidence": confidence,
                            "reply_text": ""        # no reply for complaints
                        }
                    
                    if confidence < 0.30:
                        return {
                            "is_inquiry": False,
                            "reason": f"Low confidence ({confidence:.2f})",
                            "best_match_product_id": None,
                            "confidence": confidence,
                            "reply_text": ""
                        }
                    return {
                        "is_inquiry": True,
                        "reason": str(parsed.get("reason") or ""),
                        "best_match_product_id": int(parsed["best_match_product_id"]) if parsed.get("best_match_product_id") not in (None, "") else None,
                        "confidence": confidence,
                        "reply_text": str(parsed.get("reply_text") or "")
                    }
        except Exception as e:
            print("DEBUG: Gemini call failed:", repr(e))

    # <<< UPDATED FALLBACK - Detect simple complaint keywords
    complaint_keywords = ["bad", "refund", "broken", "not working", "issue", "problem", "complain", "complaint"]
    if any(k in email_body.lower() for k in complaint_keywords):
        return {
            "is_inquiry": False,
            "is_complaint": True,   # <<< ADDED
            "reason": "Detected complaint keywords",
            "best_match_product_id": None,
            "confidence": 0.9,
            "reply_text": ""
        }
    
    # Fallback if LLM not available
    if candidates:
        confidence = candidates[0]["score"]
        if confidence < 0.5:
            return {
                "is_inquiry": False,
                "reason": f"Low confidence ({confidence:.2f})",
                "best_match_product_id": None,
                "confidence": confidence,
                "reply_text": ""
            }

        lines = [f"- {c['name']} — Rs. {c['price']} ({c['stock']} in stock)" for c in candidates]
        reply_text = f"""
Hi,

Thank you for your message.

Here are some items that may be relevant:

{chr(10).join(lines)}

Thanks,
Customer Care
"""
        return {
            "is_inquiry": True,
            "reason": "Fallback: using retrieved candidates",
            "best_match_product_id": candidates[0]["id"],
            "confidence": confidence,
            "reply_text": reply_text.strip()
        }

    # No candidates at all
    reply_text = """
Hi,

Thank you for reaching out.

We couldn't find any matching products in our catalog. Could you please provide the brand, model, or more details? We'll be happy to assist you promptly.

Thanks,
Customer Care
"""
    return {
        "is_inquiry": False,
        "reason": "No candidates found",
        "best_match_product_id": None,
        "confidence": 0.0,
        "reply_text": ""
    }
