import json
import re
from pathlib import Path

INPUT_FILE = Path("processed/amendment_notes.json")
OUTPUT_FILE = Path("processed/clean_amendment_notes.json")


TARGET_AMENDMENTS = {
    1: "First",
    24: "Twenty-fourth",
    25: "Twenty-fifth",
    42: "Forty-second",
    44: "Forty-fourth",
    52: "Fifty-second",
    61: "Sixty-first",
    73: "Seventy-third",
    74: "Seventy-fourth",
    86: "Eighty-sixth",
    91: "Ninety-first",
    93: "Ninety-third",
    101: "One Hundred and First",
    102: "One Hundred and Second",
    103: "One Hundred and Third",
    104: "One Hundred and Fourth",
    105: "One Hundred and Fifth",
    106: "One Hundred and Sixth",
}


def normalize_name(name):
    if not name:
        return None

    name = name.lower()
    name = re.sub(r"\s+", " ", name)
    name = name.replace("forty- fourth", "forty-fourth")
    name = name.replace("one hundred and fourth", "one hundred and fourth")

    return name.strip()


NORMALIZED_TARGETS = {
    normalize_name(f"Constitution ({word}) Amendment Act"): number
    for number, word in TARGET_AMENDMENTS.items()
}


def get_amendment_number(name):
    normalized = normalize_name(name)

    if not normalized:
        return None

    for target_name, number in NORMALIZED_TARGETS.items():
        if normalized == target_name:
            return number

    return None


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        notes = json.load(f)

    cleaned = []

    for note in notes:
        amendment_number = get_amendment_number(
            note.get("amendment_name")
        )

        if amendment_number is None:
            continue

        record = {
            "article": note.get("article"),
            "amendment_number": amendment_number,
            "amendment_name": (
                f"Constitution ({TARGET_AMENDMENTS[amendment_number]}"
                f" Amendment) Act"
            ),
            "amendment_year": note.get("amendment_year"),
            "section": note.get("section"),
            "effective_date": note.get("effective_date"),
            "note": note.get("note"),
        }

        cleaned.append(record)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            cleaned,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Clean amendment-note extraction completed.")
    print(f"Raw notes: {len(notes)}")
    print(f"Target notes: {len(cleaned)}")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()