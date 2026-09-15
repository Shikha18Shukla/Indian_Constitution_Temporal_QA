import pymupdf
from pathlib import Path
import subprocess
import tempfile


# ==============================
# FOLDERS
# ==============================

INPUT_DIR = Path("raw/amendments")
OUTPUT_DIR = Path("processed/amendments_raw")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# SETTINGS
# ==============================

# If normal PDF extraction gives fewer characters than this,
# we assume the PDF is scanned and use OCR.
MIN_TEXT_LENGTH = 100


# ==============================
# OCR FUNCTION
# ==============================

def ocr_page(page):
    """
    Convert a PDF page into an image and run Tesseract OCR.
    """

    pix = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2),
        alpha=False
    )

    with tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False
    ) as temp:

        image_path = temp.name

    pix.save(image_path)

    try:

        result = subprocess.run(
            [
                "tesseract",
                image_path,
                "stdout",
                "-l",
                "eng"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        return result.stdout

    finally:

        Path(image_path).unlink(missing_ok=True)


# ==============================
# PROCESS PDF
# ==============================

def process_pdf(pdf_path):

    print(f"\nProcessing: {pdf_path.name}")

    doc = pymupdf.open(pdf_path)

    # First try normal text extraction
    normal_text = ""

    for page in doc:
        normal_text += page.get_text() + "\n"

    print(f"Normal extraction: {len(normal_text)} characters")

    # ==========================
    # NORMAL PDF
    # ==========================

    if len(normal_text.strip()) >= MIN_TEXT_LENGTH:

        print("Using normal PDF text extraction.")

        final_text = normal_text

    # ==========================
    # SCANNED PDF
    # ==========================

    else:

        print("Very little text detected.")
        print("Using OCR...")

        ocr_text = ""

        for page_number, page in enumerate(doc, start=1):

            print(
                f"  OCR page {page_number}/{len(doc)}..."
            )

            ocr_text += (
                f"\n\n===== PAGE {page_number} =====\n\n"
            )

            ocr_text += ocr_page(page)

        final_text = ocr_text

    doc.close()

    return final_text


# ==============================
# MAIN
# ==============================

def main():

    pdfs = sorted(INPUT_DIR.glob("*.pdf"))

    print("Found PDFs:", len(pdfs))

    if not pdfs:

        print("No PDF files found!")

        return

    for pdf_path in pdfs:

        text = process_pdf(pdf_path)

        output_file = (
            OUTPUT_DIR /
            f"{pdf_path.stem}.txt"
        )

        output_file.write_text(
            text,
            encoding="utf-8"
        )

        print(
            f"Saved: {output_file.name}"
        )

        print(
            f"Final characters: {len(text)}"
        )

    print("\n================================")
    print("Amendment extraction complete!")
    print("================================")


if __name__ == "__main__":
    main()