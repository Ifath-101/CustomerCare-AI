from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String)
    subject = Column(String)
    is_replied = Column(Boolean, default=False)

    # ✅ NEW: Store LLM classification
    is_inquiry = Column(Boolean, default=False)
    is_complaint = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
