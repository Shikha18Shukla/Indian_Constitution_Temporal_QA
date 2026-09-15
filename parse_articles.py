import re
import json

INPUT_FILE = "constitution_raw.txt"
OUTPUT_FILE = "processed/articles.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()


# ---------------------------------------------------------
# Detect actual Article headings
# ---------------------------------------------------------
# Examples:
# 1. Name and territory of the Union.—
# 2. Admission or establishment of new States.—
# 21A. Right to education.—
#
# The important trick:
# Article headings normally have a proper legal title,
# whereas footnotes begin with things like:
# "Subs. by", "Ins. by", etc.
# ---------------------------------------------------------

article_pattern = re.compile(
    r"^\s*(\d{1,3}[A-Z]?)\.\s+(.+?)(?:—|–|-{1,2})(.*)$"
)

articles = []
current = None

# These are NOT Article headings.
footnote_starts = (
    "Subs. by",
    "Ins. by",
    "Omitted by",
    "Added by",
    "Cl. subs.",
    "Cl. ins.",
    "Cl. omitted",
)

# Some extracted lines are clearly page/header material.
ignore_exact = {
    "THE CONSTITUTION OF INDIA",
}


def valid_article_number(number):
    """
    Constitution Articles range approximately from 1 to 395.
    Allow letters such as 21A, 31A, 243A, etc.
    """
    m = re.match(r"(\d+)", number)

    if not m:
        return False

    n = int(m.group(1))

    return 1 <= n <= 395


def is_footnote_line(line):
    line = line.strip()

    if not line:
        return True

    if line in ignore_exact:
        return True

    # Normal amendment footnotes
    for prefix in footnote_starts:
        if line.startswith(prefix):
            return True

    # Footnotes often look like:
    # 1. Subs. by...
    # 2. Ins. by...
    # 3. The words...
    if re.match(r"^\d+\.\s+(Subs\.|Ins\.|Omitted|Added|The words)", line):
        return True

    return False


for line in lines:

    line = line.strip()

    if not line:
        continue

    match = article_pattern.match(line)

    if match:

        number = match.group(1)
        title = match.group(2).strip()
        first_text = match.group(3).strip()

        # Check article number
        if not valid_article_number(number):
            continue

        # Do not accept obvious footnotes as article titles
        if title.startswith(footnote_starts):
            continue

        # If there is already an Article being collected,
        # save it before starting the next one.
        if current is not None:
            articles.append(current)

        current = {
            "article_number": number,
            "title": title,
            "text": first_text
        }

        continue

    # -----------------------------------------------------
    # Lines which are not headings
    # -----------------------------------------------------

    if current is None:
        continue

    # Ignore amendment footnotes
    if is_footnote_line(line):
        continue

    # Ignore page numbers such as "2", "3", "4", etc.
    if re.fullmatch(r"\d+", line):
        continue

    # Ignore common page headers
    if line == "THE CONSTITUTION OF INDIA":
        continue

    # Ignore Part headings when they appear alone
    if re.match(r"^(PART|CHAPTER)\s+[IVXLCDM]+$", line):
        continue

    # Add remaining text to the current Article
    current["text"] += " " + line


# Save final article
if current is not None:
    articles.append(current)


# ---------------------------------------------------------
# Clean whitespace
# ---------------------------------------------------------

for article in articles:
    article["title"] = re.sub(r"\s+", " ", article["title"]).strip()
    article["text"] = re.sub(r"\s+", " ", article["text"]).strip()


# ---------------------------------------------------------
# Remove duplicate Article numbers
# ---------------------------------------------------------

unique = {}

for article in articles:

    number = article["article_number"]

    if number not in unique:
        unique[number] = article


articles = list(unique.values())


# ---------------------------------------------------------
# Sort Articles correctly
# ---------------------------------------------------------

def sort_key(article):

    m = re.match(r"(\d+)([A-Z]?)", article["article_number"])

    number = int(m.group(1))
    letter = m.group(2)

    return (number, letter)


articles.sort(key=sort_key)


# ---------------------------------------------------------
# Save JSON
# ---------------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        articles,
        f,
        ensure_ascii=False,
        indent=2
    )


# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("===================================")
print("Article extraction complete!")
print("===================================")

print("Articles extracted:", len(articles))
print("Saved to:", OUTPUT_FILE)

print("\nFirst 20 articles:\n")

for article in articles[:20]:
    print(
        article["article_number"],
        "-",
        article["title"]
    )

print("\nLast 10 articles:\n")

for article in articles[-10:]:
    print(
        article["article_number"],
        "-",
        article["title"]
    )