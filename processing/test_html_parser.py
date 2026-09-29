from processing.html_parser import parse_html_to_text
from processing.section_extractor import extract_section


FILE_PATH = (
    "data/raw/Apple_Inc./2025-10-31_10-K.html"
)


def main() -> None:
    """Verify that Risk Factors extraction has the correct boundaries."""

    text = parse_html_to_text(FILE_PATH)

    section = extract_section(
        text=text,
        start_heading_pattern=r"Item 1A\.\s*Risk Factors",
        end_heading_pattern=r"Item 1B\.\s*Unresolved Staff Comments",
    )

    print("Section extraction successful.")
    print(f"Section length: {len(section):,} characters")

    print("\n--- FIRST 5 LINES ---")

    for line in section.splitlines()[:5]:
        print(line)

    print("\n--- LAST 10 LINES ---")

    for line in section.splitlines()[-10:]:
        print(line)

    # Validate the boundary.
    assert section.lower().startswith("item 1a")

    assert (
        "item 1b. unresolved staff comments"
        not in section.lower()
    )

    print("\nBoundary validation: PASSED")


if __name__ == "__main__":
    main()