from newspaper import Article, ArticleException
from fastapi import HTTPException
import docx
import PyPDF2


def extract_from_url(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
    except ArticleException as e:
        err = str(e)
        # 403 means the site blocks bots (paywalled / anti-scrape headers)
        if "403" in err:
            raise HTTPException(
                status_code=422,
                detail=(
                    "This website blocked the request (403 Forbidden). "
                    "The page may be paywalled or bot-protected. "
                    "Try copying the article text and using the Text input instead."
                )
            )
        raise HTTPException(
            status_code=422,
            detail=f"Could not download the article: {err}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to fetch URL: {str(e)}"
        )

    if not article.text or not article.text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No text could be extracted from this URL. "
                "The page may be JavaScript-rendered or empty. "
                "Try copying the article text and using the Text input instead."
            )
        )

    return article.text


def extract_from_file(file) -> str:
    filename = file.filename
    text = ""

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file.file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from this PDF. It may be a scanned image. Please use a text-based PDF."
            )

    elif filename.endswith(".docx"):
        document = docx.Document(file.file)
        for para in document.paragraphs:
            text += para.text + "\n"

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="The uploaded DOCX file appears to be empty."
            )

    else:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "unknown"
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '.{ext}'. Please upload a PDF or DOCX file."
        )

    return text