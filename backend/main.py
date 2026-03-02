from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.verify import router as verify_router

app = FastAPI()

# Enable CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(verify_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "AI Fact Checker API"}
