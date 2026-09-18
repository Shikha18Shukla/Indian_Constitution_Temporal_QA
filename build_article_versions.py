import json
from pathlib import Path

OPERATIONS_FILE = Path("processed/amendment_operations.json")
METADATA_FILE = Path("processed/amendment_metadata.json")
OUTPUT_FILE = Path("processed/article_versions.json")


def get_effective_date(amendment, section):
    """
    Determine the effective date for an amendment operation.

    For ordinary amendments, use the amendment commencement date.

    For notification-based amendments with section-specific dates,
    use the appropriate section date when available.
    """

    # Section-specific commencement
    section_commencement = amendment.get("section_commencement")

    if section_commencement:
        section_str = str(section)

        # Exact section mapping
        if section_str in section_commencement:
            return section_commencement[section_str]

        # Handle grouped sections such as:
        # "1,2,3,4,5,..."
        for key, date in section_commencement.items():
            sections = [x.strip() for x in key.split(",")]

            if section_str in sections:
                return date

        return None

    return amendment.get("commencement_date")


def main():

    with open(OPERATIONS_FILE, "r", encoding="utf-8") as f:
        operations = json.load(f)

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    metadata_by_number = {
        item["amendment_number"]: item
        for item in metadata
    }

    # Group operations by article
    article_groups = {}

    for operation in operations:

        article = operation["article"]
        amendment_number = operation["amendment_number"]
        section = operation["section"]

        amendment = metadata_by_number.get(amendment_number)

        if not amendment:
            print(
                f"WARNING: Metadata missing for Amendment "
                f"{amendment_number}"
            )
            continue

        effective_date = get_effective_date(
            amendment,
            section
        )

        record = {
            "article": article,
            "amendment_number": amendment_number,
            "amendment_year": operation["year"],
            "section": section,
            "operation": operation["operation"],
            "effective_from": effective_date,
            "source_file": amendment["source_file"]
        }

        article_groups.setdefault(article, []).append(record)

    # Sort each article's history chronologically
    for article in article_groups:

        article_groups[article].sort(
            key=lambda x: (
                x["effective_from"] or "9999-99-99",
                x["amendment_number"]
            )
        )

    # Create version records
    versions = []

    for article, history in article_groups.items():

        for index, record in enumerate(history):

            if index == 0:
                version_number = 1
            else:
                version_number = index + 1

            effective_to = None

            # The next amendment becomes the end of this version.
            if index + 1 < len(history):
                effective_to = history[index + 1]["effective_from"]

            version = {
                "article": article,
                "version_id": f"{article}_v{version_number}",
                "version_number": version_number,
                "amendment_number": record["amendment_number"],
                "amendment_year": record["amendment_year"],
                "section": record["section"],
                "operation": record["operation"],
                "effective_from": record["effective_from"],
                "effective_to": effective_to,
                "source_file": record["source_file"]
            }

            versions.append(version)

    # Sort final dataset
    versions.sort(
        key=lambda x: (
            x["article"],
            x["version_number"]
        )
    )

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
            versions,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Total version records: {len(versions)}")
    print(f"Unique articles affected: {len(article_groups)}")


if __name__ == "__main__":
    main()