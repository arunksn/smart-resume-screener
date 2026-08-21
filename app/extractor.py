from pathlib import Path
import fitz


def extract_text_from_pdf(file_path: str) -> str:
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported by this extractor.")

    document = fitz.open(file_path)
    try:
        pages = [page.get_text("text") for page in document]
        text = "\n".join(pages).strip()
    finally:
        document.close()

    if not text:
        raise ValueError("No extractable text was found in the PDF.")
    return text


def extract_text_from_input(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        temp_path = Path("/tmp") / f"smart_resume_{abs(hash(filename))}.pdf"
        temp_path.write_bytes(content)
        try:
            return extract_text_from_pdf(str(temp_path))
        finally:
            temp_path.unlink(missing_ok=True)

    if suffix == ".txt":
        text = content.decode("utf-8", errors="ignore").strip()
        if not text:
            raise ValueError("The text resume is empty.")
        return text

    raise ValueError("Resume must be a PDF or TXT file.")
