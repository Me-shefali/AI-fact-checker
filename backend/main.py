from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models.user_model import Base
from models.factcheck_model import FactCheck

from routes.verify import router as verify_router
from routes.auth import router as auth_router
from routes.history import router as history_router


app = FastAPI(title="AI Fact Checker API")


# Create database tables automatically
Base.metadata.create_all(bind=engine)


# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(verify_router, prefix="/api", tags=["Fact Checking"])
app.include_router(history_router, prefix="/api", tags=["History"])


@app.get("/")
def read_root():
    return {
        "message": "AI Fact Checker API is running"
    }