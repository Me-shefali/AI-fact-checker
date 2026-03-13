from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from auth_dependency import get_current_user
from models.factcheck_model import FactCheck

router = APIRouter()


# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- GET LAST 50 HISTORY ----------
@router.get("/history")
def get_history(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    history = db.query(FactCheck)\
        .filter(FactCheck.user_id == user.id)\
        .order_by(FactCheck.created_at.desc())\
        .limit(50)\
        .all()

    return history