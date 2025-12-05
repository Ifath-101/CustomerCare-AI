# app/routes/email_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from app.models.product import Product
from app.services.email_reader import read_latest_unread_email
from app.services.ai_product_service import analyze_email
from app.services.auto_replier import generate_reply

router = APIRouter(prefix="/emails", tags=["Emails"])


@router.get("/process")
def process_emails(db: Session = Depends(get_db)):
    print("\n----- DEBUG: PROCESS EMAILS STARTED -----")

    email_data = read_latest_unread_email()
    print("----- DEBUG: Email Data Returned From Reader -----")
    print(email_data)

    if not email_data:
        return {"message": "No unread emails found."}

    db_products = db.query(Product).all()
    product_dicts = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "stock": p.stock,
            "price": p.price
        }
        for p in db_products
    ]

    print("----- DEBUG: Products Loaded From DB -----")
    print(product_dicts)

    print("----- DEBUG: Sending Text to AI Analyzer -----")
    print("AI INPUT TEXT:", email_data["body"])

    analysis = analyze_email(email_data["body"], product_dicts)

    print("----- DEBUG: AI Analysis Result -----")
    print(analysis)

    # <<< ADDED COMPLAINT HANDLING
    if analysis.get("is_complaint"):
        print("----- DEBUG: Email classified as COMPLAINT -----")
        from app.services.auto_replier import forward_email
        forward_email(
            original_message_id=email_data["id"],
            forward_to="ifathahamed01@gmail.com"   # <<< CHANGE THIS
        )
        return {"message": "Complaint forwarded successfully"}

    # If the analyzer says it's an inquiry AND provides a reply_text, send it
    if analysis.get("is_inquiry"):
        reply_text = analysis.get("reply_text", "").strip()
        if not reply_text:
            # fallback
            reply_text = f"""Hello,

We reviewed your inquiry but could not find a matching product in our catalog.

Thanks for reaching out!
"""

        print("----- DEBUG: Sending Reply Email Now -----")
        print("To:", email_data["from"])
        print("Subject:", f"Re: {email_data['subject']}")
        print("Reply Body:", reply_text)

        # 🔥🔥🔥 PASS CONFIDENCE + THREAD + ORIGINAL MESSAGE ID
        generate_reply(
            to_email=email_data["from"],                            # unchanged
            subject=f"Re: {email_data['subject']}",                 # unchanged
            body=reply_text,                                        # unchanged
            confidence=analysis.get("confidence", 1.0),             # <<< ADDED
            original_message_id=email_data["id"],                   # <<< ADDED
            thread_id=email_data.get("threadId")                    # <<< ADDED
        )

    else:
        print("----- DEBUG: AI Classified Email as NON-INQUIRY -----")

    return {"message": "AI processing completed successfully"}
