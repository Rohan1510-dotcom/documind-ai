from collections import Counter

from app.services.document_processor import extract_blocks_from_pdf


PDF_PATH = "uploads/resume1.pdf"


def main():
    blocks = extract_blocks_from_pdf(PDF_PATH)

    if not blocks:
        print("No blocks found.")
        return

    font_size_counter = Counter()
    font_counter = Counter()
    bold_counter = Counter()

    for block in blocks:
        for size in block.get("font_sizes", []):
            font_size_counter[round(size, 2)] += 1

        for font in block.get("fonts", []):
            font_counter[font] += 1

        bold_counter[block.get("is_bold", False)] += 1

    print("\n" + "=" * 70)
    print("DOCUMENT PROFILE")
    print("=" * 70)

    print(f"\nTotal blocks: {len(blocks)}")

    print("\nFONT SIZE DISTRIBUTION")
    print("-" * 70)

    for size, count in font_size_counter.most_common():
        print(f"{size:>8} pt : {count} spans")

    print("\nFONT DISTRIBUTION")
    print("-" * 70)

    for font, count in font_counter.most_common():
        print(f"{font:<30} : {count} spans")

    print("\nBLOCK BOLD DISTRIBUTION")
    print("-" * 70)

    for is_bold, count in bold_counter.items():
        label = "Bold" if is_bold else "Normal"
        print(f"{label:<10} : {count} blocks")

    print("\nBLOCK SUMMARY")
    print("-" * 70)

    for index, block in enumerate(blocks):
        print(f"\nBlock {index}")
        print(f"  Page: {block.get('page')}")
        print(f"  Text: {block.get('text', '')[:120]!r}")

        print(
            f"  Dominant font: "
            f"{block.get('dominant_font')}"
        )

        print(
            f"  Dominant font size: "
            f"{block.get('dominant_font_size')}"
        )

        print(
            f"  Bold span ratio: "
            f"{block.get('bold_span_ratio')}"
        )

        print(
            f"  Unique font sizes: "
            f"{block.get('unique_font_sizes')}"
        )

        print(
            f"  Unique fonts: "
            f"{block.get('unique_fonts')}"
        )

        print(
            f"  Mixed formatting: "
            f"{block.get('mixed_formatting')}"
        )

        print(
            f"  Span count: "
            f"{block.get('span_count')}"
        )


if __name__ == "__main__":
    main()