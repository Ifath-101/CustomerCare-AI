from sqlalchemy import Column, Integer, String, Text, Numeric
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    stock = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
