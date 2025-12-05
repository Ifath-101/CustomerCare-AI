from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth_routes, email_routes
from app.routes.product_routes import router as product_router
from app.routes.email_stats_routes import router as email_stats_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auto Email Reply System")

app.include_router(auth_routes.router)
app.include_router(email_routes.router)
app.include_router(product_router)
app.include_router(email_stats_router)

@app.get("/")
def home():
    return {"message": "Backend running!"}

# Allow CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
