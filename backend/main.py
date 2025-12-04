from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth_routes, email_routes
from app.routes.product_routes import router as product_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auto Email Reply System")

app.include_router(auth_routes.router)
app.include_router(email_routes.router)
app.include_router(product_router)

@app.get("/")
def home():
    return {"message": "Backend running!"}
