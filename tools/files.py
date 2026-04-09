"""File text extraction — supports txt, md, pdf, docx."""

import io


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Extract plain text from an uploaded file. Returns text content."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext in ("txt", "md", "csv", "rst"):
        return file_bytes.decode("utf-8", errors="replace")

    if ext == "pdf":
        return _extract_pdf(file_bytes)

    if ext == "docx":
        return _extract_docx(file_bytes)

    raise ValueError(f"Unsupported file type: .{ext}")


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _extract_docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
