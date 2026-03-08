from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from services.extractor import extract_from_url, extract_from_file
from services.preprocessor import preprocess_text
from services.claim_extractor import extract_claims
from services.verifier import verify_claims

router = APIRouter()


# ---------- Request Schemas ----------
class ClaimRequest(BaseModel):
    text: str


class URLRequest(BaseModel):
    url: str


# ---------- TEXT VERIFICATION ----------
@router.post("/verify")
async def verify_claim(request: ClaimRequest):
    clean_text = preprocess_text(request.text)

    claims = extract_claims(clean_text)

    results = verify_claims(claims)

    return {
        "input_type": "text",
        "claims": claims,
        "results": results
    }
    # try:
    #     clean_text = preprocess_text(request.text)

    #     claims = extract_claims(clean_text)

    #     results = verify_claims(claims)

    #     return {
    #         "input_type": "text",
    #         "claims": claims,
    #         "results": results
    #     }

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


# ---------- URL VERIFICATION ----------
@router.post("/verify/url")
async def verify_url(request: URLRequest):

    try:
        extracted_text = extract_from_url(request.url)

        clean_text = preprocess_text(extracted_text)

        claims = extract_claims(clean_text)

        results = verify_claims(claims)

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
async def verify_file(file: UploadFile = File(...)):

    try:
        extracted_text = extract_from_file(file)

        clean_text = preprocess_text(extracted_text)

        claims = extract_claims(clean_text)

        results = verify_claims(claims)

        return {
            "input_type": "file",
            "filename": file.filename,
            "claims": claims,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))