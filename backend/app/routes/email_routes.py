from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from app.models.product import Product
from app.models.email_log import EmailLog
from app.services.email_reader import read_latest_unread_email, get_unread_email_count
from app.services.ai_product_service import analyze_email
from app.services.auto_replier import generate_reply, forward_email

router = APIRouter(prefix="/emails", tags=["Emails"])


@router.get("/unread-count")
def unread_count():
    """
    Returns total unread Gmail messages (no LLM, no processing)
    """
    count = get_unread_email_count()
    return {"unread": count}


@router.get("/process")
def process_emails(db: Session = Depends(get_db)):
    print("\n----- DEBUG: PROCESS EMAILS STARTED -----")

    email_data = read_latest_unread_email()
    print("----- DEBUG: Email Data Returned From Reader -----")
    print(email_data)

    if not email_data:
        return {"message": "No unread emails found."}

    # ---- AI ANALYSIS ----
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

    analysis = analyze_email(email_data["body"], product_dicts)
    print("----- DEBUG: AI Analysis Result -----")
    print(analysis)

    # ---- SAVE EMAIL to LOG with AI classification ----
    email_log_entry = EmailLog(
        email_id=email_data["id"],
        subject=email_data["subject"],
        is_replied=False,
        is_inquiry=analysis.get("is_inquiry", False),
        is_complaint=analysis.get("is_complaint", False)
    )
    db.add(email_log_entry)
    db.commit()
    db.refresh(email_log_entry)
    print("----- DEBUG: Saved email log entry -----")

    # ------------- COMPLAINT HANDLING -------------
    if analysis.get("is_complaint"):
        print("----- DEBUG: Email classified as COMPLAINT -----")
        forward_email(
            original_message_id=email_data["id"],
            forward_to="ifathahamed01@gmail.com"
        )
        email_log_entry.is_replied = True
        db.commit()
        return {"message": "Complaint forwarded successfully"}

    # ------------- INQUIRY REPLY HANDLING -------------
    if analysis.get("is_inquiry"):
        reply_text = analysis.get("reply_text", "").strip()
        if not reply_text:
            reply_text = (
                "Hello,\n\n"
                "We reviewed your inquiry but could not find a matching product.\n\n"
                "Thanks!"
            )
        generate_reply(
            to_email=email_data["from"],
            subject=f"Re: {email_data['subject']}",
            body=reply_text,
            confidence=analysis.get("confidence", 1.0),
            original_message_id=email_data["id"],
            thread_id=email_data.get("threadId")
        )
        email_log_entry.is_replied = True
        db.commit()
    else:
        print("----- DEBUG: AI Classified Email as NON-INQUIRY -----")

    return {"message": "AI processing completed successfully"}
