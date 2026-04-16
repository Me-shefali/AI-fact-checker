from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import traceback

from services.extractor import extract_from_url, extract_from_file
from services.preprocessor import preprocess_text
from services.claim_extractor import extract_claims
from services.verifier import verify_claim as verify_single_claim  # ✅ rename
from utils.util import validate_input_text, validate_url, is_english_text

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
    top_evidence = item.get("evidence", [])
    first = top_evidence[0] if top_evidence else {}

    return FactCheck(
        user_id=user_id,
        claim=item["claim"],

        similarity=float(item.get("similarity", 0.0)) if item.get("similarity") is not None else None,
        confidence=float(item.get("confidence", 0.0)) if item.get("confidence") is not None else None,

        verdict=item["verdict"],
        evidence_text=first.get("text", "")[:1000] if first.get("text") else None,
        evidence_url=first.get("url") or None,
        evidence_source=first.get("domain") or None,  # ✅ FIX
    )


# ---------- TEXT VERIFICATION ----------
@router.post("/verify")
async def verify_text(
    request: ClaimRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        print("\nINPUT TEXT:", request.text)

        valid, error = validate_input_text(request.text)
        if not valid:
            raise HTTPException(status_code=422, detail=error)

        if not is_english_text(request.text):
            raise HTTPException(
                status_code=422,
                detail="Only English-language input is supported. Please submit English text, URL, or PDF/DOCX content."
            )

        clean_text = preprocess_text(request.text)
        claims = extract_claims(clean_text)

        print("\nEXTRACTED CLAIMS:", claims)

        if not claims:
            return {"input_type": "text", "claims": [], "results": []}

        results = []

        # ✅ FIX: loop over each claim
        for claim in claims:
            result = verify_single_claim(claim)  # correct function
            results.append(result)

            record = build_record(user.id, result)
            db.add(record)

        db.commit()

        return {
            "input_type": "text",
            "claims": claims,
            "results": results
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---------- URL VERIFICATION ----------
@router.post("/verify/url")
async def verify_url(
    request: URLRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        valid, error = validate_url(request.url)
        if not valid:
            raise HTTPException(status_code=422, detail=error)

        extracted_text = extract_from_url(request.url)

        if not is_english_text(extracted_text):
            raise HTTPException(
                status_code=422,
                detail="Only English-language sources are supported. The extracted content from this URL does not appear to be English."
            )

        clean_text = preprocess_text(extracted_text)
        claims = extract_claims(clean_text)

        if not claims:
            return {"input_type": "url", "url": request.url, "claims": [], "results": []}

        results = []

        for claim in claims:
            result = verify_single_claim(claim)
            results.append(result)

            record = build_record(user.id, result)
            db.add(record)

        db.commit()

        return {
            "input_type": "url",
            "url": request.url,
            "claims": claims,
            "results": results
        }

    except Exception as e:
        traceback.print_exc()
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

        if not is_english_text(extracted_text):
            raise HTTPException(
                status_code=422,
                detail="Only English-language PDF/DOCX files are supported. The extracted content does not appear to be English."
            )

        clean_text = preprocess_text(extracted_text)
        claims = extract_claims(clean_text)

        claims = claims[:10]  # limit

        if not claims:
            return {"input_type": "file", "filename": file.filename, "claims": [], "results": []}

        results = []

        for claim in claims:
            result = verify_single_claim(claim)
            results.append(result)

            record = build_record(user.id, result)
            db.add(record)

        db.commit()

        return {
            "input_type": "file",
            "filename": file.filename,
            "claims": claims,
            "results": results
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))