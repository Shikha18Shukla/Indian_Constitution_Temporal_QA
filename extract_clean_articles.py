import json
import re
from pathlib import Path

INPUT_FILE = Path("constitution_raw.txt")
OUTPUT_FILE = Path("processed/articles_clean.json")


# ---------------------------------------------------------
# 1. Find the actual beginning of the Constitution
# ---------------------------------------------------------

START_PATTERN = re.compile(
    r"PART I\s+THE UNION AND ITS TERRITORY\s+"
    r"1\.\s+Name and territory of the Union",
    re.MULTILINE
)


# ---------------------------------------------------------
# 2. Article heading pattern
#
# Supports:
#   1.
#   2.
#   21A.
#   239AA.
#   342A.
#   371F.
#   etc.
# ---------------------------------------------------------

ARTICLE_HEADING = re.compile(
    r"^(\d{1,3}[A-Z]{0,3})\.\s+(.+)$"
)


def clean_line(line):
    """Normalize whitespace while preserving legal text."""

    line = line.replace("\u00ad", "")

    # Replace tabs with spaces
    line = line.replace("\t", " ")

    # Collapse repeated spaces
    line = re.sub(r" +", " ", line)

    return line.strip()


# ---------------------------------------------------------
# 3. Detect actual Article headings
# ---------------------------------------------------------

def is_real_article_heading(line):

    match = ARTICLE_HEADING.match(line)

    if not match:
        return False

    article_number = match.group(1)
    title = match.group(2).strip()

    # -----------------------------------------------------
    # Reject obvious footnotes
    # -----------------------------------------------------

    footnote_patterns = [
        r"^Subs\.",
        r"^Sub-clause",
        r"^Ins\.",
        r"^Added by",
        r"^Omitted by",
        r"^The words",
        r"^Certain words",
        r"^See ",
        r"^Art\.",
        r"^Arts\.",
        r"^Cl\.",
        r"^Cls\.",
        r"^Proviso",
        r"^Paragraph",
        r"^In exercise",
        r"^The bracket",
        r"^The word",
    ]

    for pattern in footnote_patterns:

        if re.match(
            pattern,
            title,
            re.IGNORECASE
        ):
            return False

    # -----------------------------------------------------
    # Reject very short / suspicious headings
    # -----------------------------------------------------

    if len(title) < 4:
        return False

    # -----------------------------------------------------
    # Article number must be within Constitution range
    # -----------------------------------------------------

    numeric_part = re.match(
        r"\d+",
        article_number
    )

    if not numeric_part:
        return False

    number = int(
        numeric_part.group()
    )

    if number < 1 or number > 395:
        return False

    return True


# ---------------------------------------------------------
# 4. Main extraction
# ---------------------------------------------------------

def main():

    print("Reading Constitution text...")

    text = INPUT_FILE.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    # -----------------------------------------------------
    # Find actual Constitution beginning
    # -----------------------------------------------------

    start_match = START_PATTERN.search(text)

    if not start_match:

        raise RuntimeError(
            "Could not find the beginning of the Constitution."
        )

    start = start_match.start()

    print(
        f"Constitution body starts at character: {start}"
    )

    # -----------------------------------------------------
    # Find Article 395
    # -----------------------------------------------------

    article_395_pattern = re.compile(
        r"(?m)^395\.\s+Repeals\."
    )

    article_395_match = article_395_pattern.search(
        text,
        start
    )

    if not article_395_match:

        raise RuntimeError(
            "Could not find Article 395."
        )

    print(
        "Article 395 found."
    )

    # -----------------------------------------------------
    # Find First Schedule AFTER Article 395
    # -----------------------------------------------------

    end_match = re.search(
        r"(?m)^\s*(?:1\[)?FIRST SCHEDULE",
        text[
            article_395_match.start():
        ],
        re.IGNORECASE
    )

    if not end_match:

        raise RuntimeError(
            "Could not find First Schedule after Article 395."
        )

    end = (
        article_395_match.start()
        + end_match.start()
    )

    print(
        f"Constitution body ends at character: {end}"
    )

    # -----------------------------------------------------
    # Extract Constitution body
    # -----------------------------------------------------

    constitution = text[
        start:end
    ]

    # -----------------------------------------------------
    # Split into lines
    # -----------------------------------------------------

    lines = constitution.splitlines()

    # Normalize lines
    lines = [
        clean_line(line)
        for line in lines
    ]

    # -----------------------------------------------------
    # Extract articles
    # -----------------------------------------------------

    articles = []

    current = None

    for line in lines:

        if not line:
            continue

        # -------------------------------------------------
        # Check whether this is an Article heading
        # -------------------------------------------------

        if is_real_article_heading(line):

            match = ARTICLE_HEADING.match(line)

            article_number = match.group(1)
            title = match.group(2).strip()

            # ---------------------------------------------
            # Save previous article
            # ---------------------------------------------

            if current is not None:

                current["text"] = " ".join(
                    current["text"]
                ).strip()

                articles.append(current)

            # ---------------------------------------------
            # Start new article
            # ---------------------------------------------

            current = {
                "article_number": article_number,
                "title": title,
                "text": []
            }

        else:

            # Add line to current article
            if current is not None:

                current["text"].append(line)

    # -----------------------------------------------------
    # Save final article
    # -----------------------------------------------------

    if current is not None:

        current["text"] = " ".join(
            current["text"]
        ).strip()

        articles.append(current)

    # -----------------------------------------------------
    # Remove duplicate article records
    # -----------------------------------------------------

    cleaned = []

    seen_articles = set()

    for article in articles:

        article_number = article[
            "article_number"
        ]

        # Only one record per article number
        if article_number in seen_articles:
            continue

        seen_articles.add(
            article_number
        )

        cleaned.append(article)

    # -----------------------------------------------------
    # Save JSON
    # -----------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cleaned,
            f,
            indent=2,
            ensure_ascii=False
        )

    # -----------------------------------------------------
    # Verification
    # -----------------------------------------------------

    print()
    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print(
        f"Total extracted records: {len(cleaned)}"
    )

    print()
    print(
        "First 20 extracted articles:"
    )

    for article in cleaned[:20]:

        print(
            article["article_number"],
            "-",
            article["title"]
        )

    # -----------------------------------------------------
    # Specifically verify Articles 1-5
    # -----------------------------------------------------

    print()
    print(
        "Articles 1-5 verification:"
    )

    for article in cleaned:

        if article["article_number"] in {
            "1",
            "2",
            "3",
            "4",
            "5"
        }:

            print()
            print(
                "Article",
                article["article_number"]
            )

            print(
                "Title:",
                article["title"]
            )

            print(
                "Text preview:",
                article["text"][:300]
            )

    # -----------------------------------------------------
    # Check for obvious footnote contamination
    # -----------------------------------------------------

    print()
    print(
        "Checking for obvious footnote contamination..."
    )

    suspicious = []

    for article in cleaned:

        text_lower = article[
            "text"
        ].lower()

        if (
            "subs. by the constitution" in text_lower
            or "ins. by the constitution" in text_lower
            or "added by the constitution" in text_lower
        ):

            suspicious.append(
                article["article_number"]
            )

    if suspicious:

        print(
            "WARNING: possible footnote contamination in:"
        )

        print(
            suspicious
        )

    else:

        print(
            "No obvious footnote contamination detected."
        )


if __name__ == "__main__":
    main()