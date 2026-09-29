from processing.html_parser import parse_html_to_text
from processing.section_extractor import extract_major_sections


FILE_PATH = (
    "data/raw/Apple_Inc./2025-10-31_10-K.html"
)


def main() -> None:
    text = parse_html_to_text(FILE_PATH)

    sections = extract_major_sections(text)

    print("Major section extraction successful.\n")

    for name, section in sections.items():

        print("=" * 80)
        print(name.upper())
        print("=" * 80)

        print(
            f"Characters: {len(section):,}"
        )

        print("\nFirst 300 characters:")
        print(section[:300])

        print("\nLast 200 characters:")
        print(section[-200:])

        print()


if __name__ == "__main__":
    main()