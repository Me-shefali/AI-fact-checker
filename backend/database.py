import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load env variables
load_dotenv()

# Use SQLite for easier local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./factchecker.db")

# If it's a postgres URL but we want sqlite as fallback, handle it
if DATABASE_URL.startswith("postgresql"):
    # If the user really wants postgres they should have it in .env
    # But for "running the app" easily, sqlite is better.
    # We will stick to what's in .env if it exists, otherwise use sqlite.
    pass

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()