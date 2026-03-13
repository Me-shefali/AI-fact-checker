from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from services.extractor import extract_from_url, extract_from_file
from services.preprocessor import preprocess_text
from services.claim_extractor import extract_claims
from services.verifier import verify_claims

from database import SessionLocal
from auth_dependency import get_current_user
from models.factcheck_model import FactCheck

router = APIRouter()


# ---------- Database Dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Request Schemas ----------
class ClaimRequest(BaseModel):
    text: str


class URLRequest(BaseModel):
    url: str


# ---------- TEXT VERIFICATION ----------
@router.post("/verify")
async def verify_claim(
    request: ClaimRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    clean_text = preprocess_text(request.text)

    claims = extract_claims(clean_text)

    results = verify_claims(claims)

    # Save results to database
    for item in results:
        record = FactCheck(
            user_id=user.id,
            claim=item["claim"],
            similarity=item["similarity"],
            verdict=item["verdict"]
        )

        db.add(record)

    db.commit()

    return {
        "input_type": "text",
        "claims": claims,
        "results": results
    }


# ---------- URL VERIFICATION ----------
@router.post("/verify/url")
async def verify_url(
    request: URLRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        extracted_text = extract_from_url(request.url)

        clean_text = preprocess_text(extracted_text)

        claims = extract_claims(clean_text)

        results = verify_claims(claims)

        for item in results:
            record = FactCheck(
                user_id=user.id,
                claim=item["claim"],
                similarity=item["similarity"],
                verdict=item["verdict"]
            )

            db.add(record)

        db.commit()

        return {
            "input_type": "url",
            "url": request.url,
            "claims": claims,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- FILE VERIFICATION ----------
@router.post("/verify/file")
async def verify_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    try:
        extracted_text = extract_from_file(file)

        clean_text = preprocess_text(extracted_text)

        claims = extract_claims(clean_text)

        results = verify_claims(claims)

        for item in results:
            record = FactCheck(
                user_id=user.id,
                claim=item["claim"],
                similarity=item["similarity"],
                verdict=item["verdict"]
            )

            db.add(record)

        db.commit()

        return {
            "input_type": "file",
            "filename": file.filename,
            "claims": claims,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))