from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String)
    subject = Column(String)
    is_replied = Column(Boolean, default=False)
