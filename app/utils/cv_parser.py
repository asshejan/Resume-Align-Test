from typing import Optional
from PyPDF2 import PdfReader
from docx import Document
import io

def extract_text_from_pdf(file_bytes: bytes) -> Optional[str]:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return None

def extract_text_from_docx(file_bytes: bytes) -> Optional[str]:
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = " ".join(para.text for para in doc.paragraphs)
        return text.strip()
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return None 