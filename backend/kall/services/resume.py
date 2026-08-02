from pathlib import Path
from docx import Document
from pypdf import PdfReader


def extract_resume_text(path: str, mime_type: str) -> str:
    file_path = Path(path)
    if mime_type == "application/pdf":
        return "\n".join(page.extract_text() or "" for page in PdfReader(file_path).pages)
    if mime_type.endswith("wordprocessingml.document"):
        return "\n".join(p.text for p in Document(file_path).paragraphs)
    return file_path.read_text(encoding="utf-8", errors="ignore")
