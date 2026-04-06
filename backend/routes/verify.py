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


# ---------- Helper: build FactCheck record ----------
def build_record(user_id: int, item: dict) -> FactCheck:
    """
    Converts a verify_claims result dict into a FactCheck ORM record.
    Persists confidence + top evidence fields that were previously dropped.
    """
    top_evidence = item.get("evidence", [])
    first = top_evidence[0] if top_evidence else {}

    return FactCheck(
        user_id=user_id,
        claim=item["claim"],
        similarity=item["similarity"],
        verdict=item["verdict"],
        confidence=item.get("confidence"),
        evidence_text=first.get("text", "")[:1000] if first.get("text") else None,
        evidence_url=first.get("url") or None,
        evidence_source=first.get("source") or None,
    )


# ---------- TEXT VERIFICATION ----------
@router.post("/verify")
async def verify_claim(
    request: ClaimRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):  
    try:
        clean_text = preprocess_text(request.text)
        claims = extract_claims(clean_text)

        if not claims:
            return {"input_type": "text", "claims": [], "results": []}

        results = verify_claims(claims)

        for item in results:
            db.add(build_record(user.id, item))
        db.commit()

        return {
            "input_type": "text",
            "claims": claims,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- URL VERIFICATION ----------
@router.post("/verify/url")
async def verify_url(
    request: URLRequest,
    user=Depends(get_current_user),          # FIX: was missing auth check
    db: Session = Depends(get_db)
):
    try:
        extracted_text = extract_from_url(request.url)
        clean_text = preprocess_text(extracted_text)
        claims = extract_claims(clean_text)

        if not claims:
            return {"input_type": "url", "url": request.url, "claims": [], "results": []}

        results = verify_claims(claims)

        for item in results:
            db.add(build_record(user.id, item))
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

        MAX_CLAIMS = 10  # don't verify more than 10 per request
        claims = claims[:MAX_CLAIMS]

        if not claims:
            return {"input_type": "file", "filename": file.filename, "claims": [], "results": []}

        results = verify_claims(claims)

        for item in results:
            db.add(build_record(user.id, item))
        db.commit()

        return {
            "input_type": "file",
            "filename": file.filename,
            "claims": claims,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))