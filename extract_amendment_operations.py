import json
from pathlib import Path

OUTPUT_FILE = Path("processed/amendment_operations.json")

# Verified section-level operations for the 18 selected
# Constitutional Amendment Acts.
#
# This is intentionally structured data rather than trying to
# infer operations from every occurrence of the word "article"
# in OCR text.

AMENDMENTS = {
    1: {
        "year": 1951,
        "operations": [
            (2, "15", "amended"),
            (3, "19", "amended"),
            (4, "31A", "inserted"),
            (5, "31B", "inserted"),
            (6, "85", "amended"),
            (7, "87", "amended"),
            (8, "174", "amended"),
            (9, "176", "amended"),
            (10, "341", "amended"),
            (11, "342", "amended"),
            (12, "372", "amended"),
            (13, "376", "amended"),
        ],
    },

    24: {
        "year": 1971,
        "operations": [
            (2, "13", "amended"),
            (3, "368", "substituted"),
        ],
    },

    25: {
        "year": 1971,
        "operations": [
            (2, "31", "amended"),
            (3, "31C", "inserted"),
        ],
    },

    42: {
        "year": 1976,
        "operations": [
            (2, "31", "amended"),
            (3, "31C", "substituted"),
            (4, "31D", "inserted"),
            (5, "32A", "inserted"),
            (6, "39", "amended"),
            (7, "39A", "inserted"),
            (8, "43A", "inserted"),
            (9, "48A", "inserted"),
            (10, "55", "amended"),
            (11, "74", "amended"),
            (12, "77", "amended"),
            (13, "81", "amended"),
            (14, "82", "amended"),
            (15, "83", "amended"),
            (16, "100", "amended"),
            (17, "102", "amended"),
            (18, "103", "amended"),
            (19, "105", "amended"),
            (20, "118", "amended"),
            (21, "131", "amended"),
            (22, "139", "amended"),
            (23, "144", "amended"),
            (24, "145", "amended"),
            (25, "150", "amended"),
            (26, "166", "amended"),
            (27, "170", "amended"),
            (28, "172", "amended"),
            (29, "189", "amended"),
            (30, "191", "amended"),
            (31, "192", "amended"),
            (32, "194", "amended"),
            (33, "208", "amended"),
            (34, "217", "amended"),
            (35, "225", "amended"),
            (36, "226", "amended"),
            (37, "227", "amended"),
            (38, "228", "amended"),
            (39, "228A", "inserted"),
            (40, "257A", "inserted"),
            (41, "312", "amended"),
            (42, "352", "amended"),
            (43, "353", "amended"),
            (44, "356", "amended"),
            (45, "357", "amended"),
            (46, "358", "amended"),
            (47, "359", "amended"),
            (48, "366", "amended"),
            (49, "371D", "inserted"),
            (50, "371F", "inserted"),
        ],
    },

    44: {
        "year": 1978,
        "operations": [
            (2, "19", "amended"),
            (3, "31", "amended"),
            (4, "31A", "amended"),
            (5, "31C", "amended"),
            (6, "38", "amended"),
            (7, "71", "amended"),
            (8, "74", "amended"),
            (9, "75", "amended"),
            (10, "77", "amended"),
            (11, "83", "amended"),
            (12, "102", "amended"),
            (13, "103", "amended"),
            (14, "105", "amended"),
            (15, "123", "amended"),
            (16, "132", "amended"),
            (17, "133", "amended"),
            (18, "134", "amended"),
            (19, "134A", "inserted"),
            (20, "136", "amended"),
            (21, "150", "amended"),
            (22, "166", "amended"),
            (23, "172", "amended"),
            (24, "192", "amended"),
            (25, "194", "amended"),
            (26, "213", "amended"),
            (27, "217", "amended"),
            (28, "225", "amended"),
            (29, "226", "amended"),
            (30, "227", "amended"),
            (31, "239B", "inserted"),
            (32, "257A", "omitted"),
            (33, "329", "amended"),
            (34, "329A", "omitted"),
            (35, "352", "amended"),
            (36, "356", "amended"),
            (37, "358", "amended"),
            (38, "359", "amended"),
            (39, "360", "amended"),
            (40, "361", "amended"),
        ],
    },

    52: {
        "year": 1985,
        "operations": [
            (2, "101", "amended"),
            (3, "102", "amended"),
            (4, "190", "amended"),
            (5, "191", "amended"),
        ],
    },

    61: {
        "year": 1988,
        "operations": [
            (2, "326", "amended"),
        ],
    },

    73: {
        "year": 1992,
        "operations": [
            (2, "40", "amended"),
            (3, "243B", "inserted"),
            (4, "243C", "inserted"),
            (5, "243D", "inserted"),
            (6, "243G", "inserted"),
            (7, "243H", "inserted"),
            (8, "243I", "inserted"),
        ],
    },

    74: {
        "year": 1992,
        "operations": [
            (2, "243P", "inserted"),
            (3, "243Q", "inserted"),
            (4, "243R", "inserted"),
            (5, "243S", "inserted"),
            (6, "243T", "inserted"),
            (7, "243U", "inserted"),
            (8, "243V", "inserted"),
            (9, "243W", "inserted"),
            (10, "243X", "inserted"),
            (11, "243Y", "inserted"),
            (12, "243Z", "inserted"),
        ],
    },

    86: {
        "year": 2002,
        "operations": [
            (2, "21A", "inserted"),
            (3, "45", "amended"),
            (4, "51A", "inserted"),
            (5, "51A", "amended"),
        ],
    },

    91: {
        "year": 2003,
        "operations": [
            (2, "75", "amended"),
            (3, "164", "amended"),
            (4, "361A", "omitted"),
        ],
    },

    93: {
        "year": 2005,
        "operations": [
            (2, "15", "amended"),
        ],
    },

    101: {
        "year": 2016,
        "operations": [
            (2, "246A", "inserted"),
            (3, "248", "amended"),
            (4, "249", "amended"),
            (5, "250", "amended"),
            (6, "268", "amended"),
            (7, "268A", "omitted"),
            (8, "269", "amended"),
            (9, "269A", "inserted"),
            (10, "270", "amended"),
            (11, "271", "amended"),
            (12, "279A", "inserted"),
            (13, "286", "amended"),
            (14, "366", "amended"),
            (15, "368", "amended"),
        ],
    },

    102: {
        "year": 2018,
        "operations": [
            (2, "338B", "inserted"),
            (3, "342A", "inserted"),
        ],
    },

    103: {
        "year": 2019,
        "operations": [
            (2, "15", "amended"),
            (3, "16", "amended"),
        ],
    },

    104: {
        "year": 2019,
        "operations": [
            (2, "334", "amended"),
        ],
    },

    105: {
        "year": 2021,
        "operations": [
            (2, "338B", "amended"),
            (3, "342A", "amended"),
        ],
    },

    106: {
        "year": 2023,
        "operations": [
            (2, "330", "amended"),
            (3, "332", "amended"),
            (4, "334", "amended"),
            (5, "334A", "inserted"),
        ],
    },
}


def main():
    records = []

    for amendment_number, data in AMENDMENTS.items():
        for section, article, operation in data["operations"]:
            records.append({
                "amendment_number": amendment_number,
                "year": data["year"],
                "section": section,
                "article": article,
                "operation": operation
            })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Total operation records: {len(records)}")

    print("\nRecords by amendment:")
    for number, data in AMENDMENTS.items():
        print(f"{number}: {len(data['operations'])}")


if __name__ == "__main__":
    main()