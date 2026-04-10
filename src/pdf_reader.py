"""Read PDF files from the input directory and extract their text content."""

from pathlib import Path

from PyPDF2 import PdfReader


INPUT_DIR = Path(__file__).resolve().parent.parent / "input"


def extract_text(pdf_path: Path) -> str:
    """Extract all text from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Concatenated text from every page, separated by newlines.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a PDF or contains no extractable text.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {pdf_path}")

    reader = PdfReader(pdf_path)
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    if not pages:
        raise ValueError(f"No extractable text found in {pdf_path}")

    return "\n\n".join(pages)


def list_pdfs(directory: Path | None = None) -> list[Path]:
    """List all PDF files in the given directory (defaults to INPUT_DIR).

    Returns:
        Sorted list of PDF file paths.
    """
    directory = directory or INPUT_DIR
    return sorted(directory.glob("*.pdf"))
