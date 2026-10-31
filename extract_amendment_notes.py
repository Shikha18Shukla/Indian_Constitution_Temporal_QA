import json
import re
from pathlib import Path

INPUT_FILE = Path("processed/articles_clean.json")
OUTPUT_FILE = Path("processed/amendment_notes.json")


# Patterns that usually indicate the beginning of an
# amendment/history annotation inside the consolidated Constitution.
NOTE_START = re.compile(
    r"(?i)"
    r"(?:"
    r"Subs\.|"
    r"Ins\.|"
    r"Added by|"
    r"Omitted by|"
    r"The words|"
    r"Certain words|"
    r"See |"
    r"Art\.|"
    r"Arts\.|"
    r"Cl\.|"
    r"Cls\.|"
    r"Proviso|"
    r"The bracket|"
    r"The word|"
    r"Original Part|"
    r"Part "
    r")"
)

AMENDMENT_PATTERN = re.compile(
    r"Constitution\s*\(([^)]+?\s+Amendment)\)\s*Act,?\s*(\d{4})",
    re.IGNORECASE
)

SECTION_PATTERN = re.compile(
    r"(?:section|s\.)\s*(\d+[A-Za-z]?)",
    re.IGNORECASE
)


DATE_PATTERN = re.compile(
    r"w\.e\.f\.\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})",
    re.IGNORECASE
)


def normalize_date(match):
    day = int(match.group(1))
    month = int(match.group(2))
    year = int(match.group(3))

    return f"{year:04d}-{month:02d}-{day:02d}"


def extract_notes(article_text):
    """
    Extract amendment-history annotations from one article.
    This is a preliminary extraction step; results must be validated.
    """

    matches = list(NOTE_START.finditer(article_text))

    if not matches:
        return []

    notes = []

    for i, match in enumerate(matches):
        start = match.start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(article_text)

        note = article_text[start:end].strip()

        # Ignore extremely short fragments.
        if len(note) < 15:
            continue

        amendment_match = AMENDMENT_PATTERN.search(note)
        section_match = SECTION_PATTERN.search(note)
        date_match = DATE_PATTERN.search(note)

        amendment_name = None
        amendment_year = None
        section = None
        effective_date = None

        if amendment_match:
            amendment_name = (
                "Constitution ("
                + amendment_match.group(1).strip()
                + ") Act"
            )
            amendment_year = int(amendment_match.group(2))

        if section_match:
            section = section_match.group(1)

        if date_match:
            effective_date = normalize_date(date_match)

        notes.append(
            {
                "amendment_name": amendment_name,
                "amendment_year": amendment_year,
                "section": section,
                "effective_date": effective_date,
                "note": note,
            }
        )

    return notes


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    results = []

    for article in articles:
        article_number = article.get("article_number")

        text = article.get("text", "")

        notes = extract_notes(text)

        for note in notes:
            record = {
                "article": article_number,
                **note,
            }

            results.append(record)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Amendment-note extraction completed.")
    print(f"Input articles: {len(articles)}")
    print(f"Extracted notes: {len(results)}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()