# app/routes/product_routes.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db,engine, Session
from app.models.product import Product
from app.services.embedding_service import build_faiss_index
from typing import List, Tuple
from pydantic import BaseModel
from decimal import Decimal
import threading

router = APIRouter(prefix="/products", tags=["Products"])


# === Pydantic Schemas for request validation ===
from pydantic import BaseModel
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    stock: int
    price: float

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    stock: int | None = None
    price: float | None = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    stock: int
    price: float

    class Config:
        from_attributes = True


# === Background task to rebuild FAISS index ===
def rebuild_faiss_index_background(db_session_factory):
    """
    Runs in a separate thread so API response is instant.
    Uses a new DB session to avoid conflicts.
    """
    def task():
        db = db_session_factory()
        try:
            products = db.query(Product).all()
            items: List[Tuple[int, str]] = []
            for p in products:
                text = f"{p.name}. {p.description or ''}".strip()
                if text:
                    items.append((p.id, text))
            
            if items:
                build_faiss_index(items)
                print(f"FAISS index auto-rebuilt with {len(items)} products")
            else:
                print("No products found during auto-rebuild")
        except Exception as e:
            print(f"Error during auto FAISS rebuild: {e}")
        finally:
            db.close()

    threading.Thread(target=task, daemon=True).start()


# === ROUTES ===

@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_product = Product(
        name=product.name,
        description=product.description,
        stock=product.stock,
        price=Decimal(str(product.price))  # safe float → Decimal
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Auto-rebuild index in background
    rebuild_faiss_index_background(lambda: Session(bind=engine))

    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "price" and value is not None:
            setattr(db_product, key, Decimal(str(value)))
        else:
            setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)

    # Auto-rebuild index
    rebuild_faiss_index_background(lambda: Session(bind=engine))

    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()

    # Auto-rebuild after delete
    rebuild_faiss_index_background(lambda: Session(bind=engine))

    return {"message": "Product deleted successfully"}


@router.post("/build-index")
def build_index_manual(db: Session = Depends(get_db)):
    """
    Manual rebuild — useful for first time or recovery
    """
    products = db.query(Product).all()
    items: List[Tuple[int, str]] = []
    for p in products:
        text = f"{p.name}. {p.description or ''}".strip()
        if text:
            items.append((p.id, text))

    if not items:
        return {"status": "warning", "message": "No products to index"}

    build_faiss_index(items)
    return {"status": "ok", "count": len(items), "message": "FAISS index rebuilt manually"}