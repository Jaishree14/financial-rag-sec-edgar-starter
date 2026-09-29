from processing.html_parser import parse_html_to_text


FILE_PATH = "data/raw/Apple_Inc./2025-10-31_10-K.html"


def main():
    text = parse_html_to_text(FILE_PATH)
    lines = text.splitlines()

    print("Lines containing 'Item 7':")
    print()

    for i, line in enumerate(lines):
        if "Item 7" in line:
            print(f"Line {i}: {repr(line)}")
            print("Next lines:")
            for j in range(i + 1, min(i + 5, len(lines))):
                print(f"Line {j}: {repr(lines[j])}")
            print("-" * 80)


if __name__ == "__main__":
    main()