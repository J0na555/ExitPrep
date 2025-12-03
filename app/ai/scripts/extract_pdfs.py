"""Extract text from PDF files.

This script loops through all PDF files in
`backend/app/ai/data/past_papers_raw/`, extracts text using `pypdf`, and
saves the extracted text in `backend/app/ai/data/past_papers_text/` with the
same filename but a `.txt` extension.

Usage:
    python extract_pdfs.py

Dependencies:
    pip install pypdf

The script creates the output directory if it does not already exist and
prints which files succeeded and which failed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a single PDF file using pypdf.

    Returns the concatenated text of all pages. If a page's text is None,
    it will be skipped.
    """
    try:
        # Import here so missing dependency is reported only when used
        from pypdf import PdfReader
    except Exception as exc:  # pragma: no cover - runtime dependency
        raise ImportError(
            "pypdf is required. Install with: pip install pypdf"
        ) from exc

    reader = PdfReader(str(pdf_path))
    pages_text = []
    for page in reader.pages:
        # extract_text() may return None for some pages
        page_text: Optional[str] = page.extract_text()
        if page_text:
            pages_text.append(page_text)

    return "\n\n".join(pages_text)


def ensure_output_dir(output_dir: Path) -> None:
    """Create the output directory if it doesn't exist."""
    output_dir.mkdir(parents=True, exist_ok=True)


def process_all_pdfs(input_dir: Path, output_dir: Path) -> None:
    """Process every .pdf file in `input_dir` and write text files to
    `output_dir`.
    """
    ensure_output_dir(output_dir)

    if not input_dir.exists():
        print(f"Input directory does not exist: {input_dir}")
        return

    pdf_paths = sorted(input_dir.glob("*.pdf"))
    if not pdf_paths:
        print(f"No PDF files found in: {input_dir}")
        return

    success = []
    failures = []

    for pdf_path in pdf_paths:
        txt_name = pdf_path.with_suffix(".txt").name
        out_path = output_dir / txt_name
        try:
            text = extract_text_from_pdf(pdf_path)
            # Write using utf-8; overwrite if exists
            out_path.write_text(text, encoding="utf-8")
            success.append(pdf_path.name)
            print(f"Extracted: {pdf_path.name} -> {out_path}")
        except Exception as exc:
            failures.append((pdf_path.name, str(exc)))
            print(f"Failed: {pdf_path.name} -> {exc}")

    # Summary
    print("\nSummary:")
    print(f"  Succeeded: {len(success)}")
    if success:
        for name in success:
            print(f"    - {name}")

    print(f"  Failed: {len(failures)}")
    if failures:
        for name, reason in failures:
            print(f"    - {name}: {reason}")


def main() -> None:
    """Entry point for the script.

    It resolves the input/output directories relative to the repository
    layout described in the task. If you run the script from elsewhere,
    the paths below are still absolute (based on the script's location).
    """
    # Resolve base directory as two levels up from this script (backend/app)
    base_dir = Path(__file__).resolve().parents[2]
    # The AI data folder lives at backend/app/ai/data
    input_dir = base_dir / "ai" / "data" / "past_papers_raw"
    output_dir = base_dir / "ai" / "data" / "past_papers_text"

    # If you want to run the script from a different working directory,
    # you can replace the two lines above with explicit paths.

    process_all_pdfs(input_dir, output_dir)


if __name__ == "__main__":
    try:
        main()
    except ImportError as imp_err:
        print(imp_err)
        sys.exit(2)
    except Exception as exc:  # pragma: no cover - top level guard
        print(f"Unexpected error: {exc}")
        sys.exit(1)
