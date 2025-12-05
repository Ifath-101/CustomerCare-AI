from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.email_log import EmailLog

router = APIRouter(prefix="/emails", tags=["Email Stats"])


@router.get("/stats")
def get_stats(filter: str = "today", db: Session = Depends(get_db)):
    now = datetime.utcnow()

    if filter == "today":
        start = now - timedelta(days=1)
    elif filter == "3days":
        start = now - timedelta(days=3)
    elif filter == "week":
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=1)

    logs = db.query(EmailLog).filter(EmailLog.created_at >= start).all()

    total = len(logs)
    inquiries = len([l for l in logs if l.is_inquiry])
    complaints = len([l for l in logs if l.is_complaint])
    replied = len([l for l in logs if l.is_replied])

    return {
        "total": total,
        "inquiries": inquiries,
        "complaints": complaints,
        "replied": replied
    }
