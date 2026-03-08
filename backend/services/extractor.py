from newspaper import Article
import docx
import PyPDF2


def extract_from_url(url):

    article = Article(url)
    article.download()
    article.parse()

    return article.text


def extract_from_file(file):

    filename = file.filename
    text = ""

    if filename.endswith(".pdf"):

        reader = PyPDF2.PdfReader(file.file)

        for page in reader.pages:
            text += page.extract_text()

    elif filename.endswith(".docx"):

        document = docx.Document(file.file)

        for para in document.paragraphs:
            text += para.text + "\n"

    return text