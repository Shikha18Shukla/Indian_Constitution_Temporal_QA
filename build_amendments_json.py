import json
import re
from pathlib import Path

INPUT_DIR = Path("processed/amendments_raw")
OUTPUT_FILE = Path("processed/amendments.json")


# Official amendment names.
# We use these instead of extracting the title from OCR text.
AMENDMENT_NAMES = {
    1: "First",
    24: "Twenty-Fourth",
    25: "Twenty-Fifth",
    42: "Forty-Second",
    44: "Forty-Fourth",
    52: "Fifty-Second",
    61: "Sixty-First",
    73: "Seventy-Third",
    74: "Seventy-Fourth",
    86: "Eighty-Sixth",
    91: "Ninety-First",
    93: "Ninety-Third",
    101: "One Hundred and First",
    102: "One Hundred and Second",
    103: "One Hundred and Third",
    104: "One Hundred and Fourth",
    105: "One Hundred and Fifth",
    106: "One Hundred and Sixth",
}


def clean_ocr_article(article):
    """Fix known OCR errors in article numbers."""

    article = article.strip().upper()

    ocr_fixes = {
        "2794": "279A",
        "3304": "330A",
        "3344": "334A",
    }

    return ocr_fixes.get(article, article)


def extract_articles(text):
    """
    Preliminary extraction of article references.

    This is NOT yet the final affected-articles dataset.
    We will verify the actual amendment operations separately.
    """

    pattern = (
        r"\barticles?\s+"
        r"([0-9]{1,3}[A-Z]?"
        r"(?:\s*(?:and|or|,)\s*[0-9]{1,3}[A-Z]?)*)"
    )

    matches = re.findall(
        pattern,
        text,
        re.IGNORECASE
    )

    articles = []

    for match in matches:

        numbers = re.findall(
            r"\d{1,3}[A-Z]?",
            match.upper()
        )

        for number in numbers:

            number = clean_ocr_article(number)

            if number not in articles:
                articles.append(number)

    return articles


def extract_metadata(file_path):

    # Read extracted amendment text
    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    # Read amendment number and year directly from filename
    match = re.match(
        r"(\d+)_Amendment_(\d{4})\.txt",
        file_path.name
    )

    if not match:
        return None

    amendment_number = int(match.group(1))
    year = int(match.group(2))

    # Use our verified amendment name
    amendment_name = AMENDMENT_NAMES.get(
        amendment_number,
        f"Amendment {amendment_number}"
    )

    title = (
        f"THE CONSTITUTION "
        f"({amendment_name.upper()} AMENDMENT) ACT, "
        f"{year}"
    )

    affected_articles = extract_articles(text)

    return {
        "amendment_number": amendment_number,
        "year": year,
        "title": title,
        "source_file": file_path.name,
        "affected_articles": affected_articles
    }


def main():

    records = []

    files = sorted(
        INPUT_DIR.glob("*.txt")
    )

    print(f"Found {len(files)} amendment files.")

    for file_path in files:

        record = extract_metadata(file_path)

        if record:

            records.append(record)

            print(
                f"Processed Amendment "
                f"{record['amendment_number']}: "
                f"{record['title']}"
            )

    # Sort by amendment number
    records.sort(
        key=lambda x: x["amendment_number"]
    )

    # Save JSON
    OUTPUT_FILE.write_text(
        json.dumps(
            records,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print()
    print("================================")
    print("amendments.json created successfully!")
    print(f"Records: {len(records)}")
    print("================================")


if __name__ == "__main__":
    main()