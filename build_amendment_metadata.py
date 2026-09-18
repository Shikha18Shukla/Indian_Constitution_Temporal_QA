import json
from pathlib import Path

OUTPUT_FILE = Path("processed/amendment_metadata.json")

# Metadata for the 18 Constitutional Amendment Acts
# used in this project.
#
# IMPORTANT:
# assent_date = date President gave assent
# commencement_date = date the Act/provisions came into force
#
# When an amendment had different commencement dates for
# different sections, we preserve that information instead
# of inventing a single date.

AMENDMENT_METADATA = [

    {
        "amendment_number": 1,
        "year": 1951,
        "title": "Constitution (First Amendment) Act, 1951",
        "assent_date": "1951-05-18",
        "commencement_date": "1951-06-18",
        "commencement_type": "specified",
        "source_file": "001_Amendment_1951.pdf"
    },

    {
        "amendment_number": 24,
        "year": 1971,
        "title": "Constitution (Twenty-fourth Amendment) Act, 1971",
        "assent_date": "1971-11-05",
        "commencement_date": "1971-11-05",
        "commencement_type": "same_day",
        "source_file": "024_Amendment_1971.pdf"
    },

    {
        "amendment_number": 25,
        "year": 1971,
        "title": "Constitution (Twenty-fifth Amendment) Act, 1971",
        "assent_date": "1971-12-20",
        "commencement_date": "1972-04-20",
        "commencement_type": "specified",
        "source_file": "025_Amendment_1971.pdf"
    },

    {
        "amendment_number": 42,
        "year": 1976,
        "title": "Constitution (Forty-second Amendment) Act, 1976",
        "assent_date": "1976-12-18",
        "commencement_date": "1977-01-03",
        "commencement_type": "specified",
        "source_file": "042_Amendment_1976.pdf"
    },

    {
        "amendment_number": 44,
        "year": 1978,
        "title": "Constitution (Forty-fourth Amendment) Act, 1978",
        "assent_date": "1979-04-30",
        "commencement_date": "1979-06-20",
        "commencement_type": "specified",
        "source_file": "044_Amendment_1978.pdf"
    },

    {
        "amendment_number": 52,
        "year": 1985,
        "title": "Constitution (Fifty-second Amendment) Act, 1985",
        "assent_date": "1985-02-15",
        "commencement_date": "1985-03-01",
        "commencement_type": "specified",
        "source_file": "052_Amendment_1985.pdf"
    },

    {
        "amendment_number": 61,
        "year": 1988,
        "title": "Constitution (Sixty-first Amendment) Act, 1988",
        "assent_date": "1989-03-28",
        "commencement_date": "1989-03-28",
        "commencement_type": "same_day",
        "source_file": "061_Amendment_1988.pdf"
    },

    {
        "amendment_number": 73,
        "year": 1992,
        "title": "Constitution (Seventy-third Amendment) Act, 1992",
        "assent_date": "1992-04-20",
        "commencement_date": "1993-04-24",
        "commencement_type": "specified",
        "source_file": "073_Amendment_1992.pdf"
    },

    {
        "amendment_number": 74,
        "year": 1992,
        "title": "Constitution (Seventy-fourth Amendment) Act, 1992",
        "assent_date": "1992-04-20",
        "commencement_date": "1993-06-01",
        "commencement_type": "specified",
        "source_file": "074_Amendment_1992.pdf"
    },

    {
        "amendment_number": 86,
        "year": 2002,
        "title": "Constitution (Eighty-sixth Amendment) Act, 2002",
        "assent_date": "2002-12-12",
        "commencement_date": "2002-12-12",
        "commencement_type": "same_day",
        "source_file": "086_Amendment_2002.pdf"
    },

    {
        "amendment_number": 91,
        "year": 2003,
        "title": "Constitution (Ninety-first Amendment) Act, 2003",
        "assent_date": "2004-01-01",
        "commencement_date": "2004-01-01",
        "commencement_type": "same_day",
        "source_file": "091_Amendment_2003.pdf"
    },

    {
        "amendment_number": 93,
        "year": 2005,
        "title": "Constitution (Ninety-third Amendment) Act, 2005",
        "assent_date": "2006-01-20",
        "commencement_date": "2006-01-20",
        "commencement_type": "same_day",
        "source_file": "093_Amendment_2005.pdf"
    },

    {
        "amendment_number": 101,
        "year": 2016,
        "title": "Constitution (One Hundred and First Amendment) Act, 2016",
        "assent_date": "2016-09-08",
        "commencement_date": None,
        "commencement_type": "notification_based",
        "section_commencement": {
            "12": "2016-09-12",
            "1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,19,20": "2016-09-16"
        },
        "source_file": "101_Amendment_2016.pdf"
    },

    {
        "amendment_number": 102,
        "year": 2018,
        "title": "Constitution (One Hundred and Second Amendment) Act, 2018",
        "assent_date": "2018-08-11",
        "commencement_date": "2018-08-15",
        "commencement_type": "specified",
        "source_file": "102_Amendment_2018.pdf"
    },

    {
        "amendment_number": 103,
        "year": 2019,
        "title": "Constitution (One Hundred and Third Amendment) Act, 2019",
        "assent_date": "2019-01-12",
        "commencement_date": "2019-01-14",
        "commencement_type": "specified",
        "source_file": "103_Amendment_2019.pdf"
    },

    {
        "amendment_number": 104,
        "year": 2019,
        "title": "Constitution (One Hundred and Fourth Amendment) Act, 2019",
        "assent_date": "2020-01-25",
        "commencement_date": "2020-01-25",
        "commencement_type": "specified",
        "source_file": "104_Amendment_2019.pdf"
    },

    {
        "amendment_number": 105,
        "year": 2021,
        "title": "Constitution (One Hundred and Fifth Amendment) Act, 2021",
        "assent_date": "2021-08-18",
        "commencement_date": "2021-08-18",
        "commencement_type": "specified",
        "source_file": "105_Amendment_2021.pdf"
    },

    {
        "amendment_number": 106,
        "year": 2023,
        "title": "Constitution (One Hundred and Sixth Amendment) Act, 2023",
        "assent_date": "2023-09-28",
        "commencement_date": None,
        "commencement_type": "notification_based",
        "source_file": "106_Amendment_2023.pdf"
    }
]


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            AMENDMENT_METADATA,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Total amendments: {len(AMENDMENT_METADATA)}")


if __name__ == "__main__":
    main()