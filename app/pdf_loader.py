from pathlib import Path
import fitz
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, DATA_DIR

def save_uploaded_file(uploaded_file, dest_path: Path):
    with open(dest_path, "wb") as f:
        f.write(uploaded_file.file.read())

def load_pdf_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    return "\n\n".join(pages)

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + chunk_size, L)
        chunk = text[start:end].strip()
        if chunk:
            metadata = {"start_char": start, "end_char": end}
            chunks.append({"text": chunk, "metadata": metadata})
        start = max(end - overlap, end)
    return chunks

def load_and_chunk(pdf_path: str):
    text = load_pdf_text(pdf_path)
    return chunk_text(text)
