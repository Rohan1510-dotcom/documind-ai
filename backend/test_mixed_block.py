import fitz


PDF_PATH = "uploads/resume1.pdf"


def main():
    document = fitz.open(PDF_PATH)

    try:
        for page_number, page in enumerate(document, start=1):
            data = page.get_text("dict")

            for block_number, block in enumerate(data["blocks"]):
                if block.get("type") != 0:
                    continue

                text = " ".join(
                    span.get("text", "").strip()
                    for line in block.get("lines", [])
                    for span in line.get("spans", [])
                    if span.get("text", "").strip()
                )

                if "Projects" not in text:
                    continue

                print("\n" + "=" * 70)
                print(f"PAGE: {page_number}")
                print(f"PDF BLOCK: {block_number}")
                print("=" * 70)

                for line_number, line in enumerate(
                    block.get("lines", [])
                ):
                    for span_number, span in enumerate(
                        line.get("spans", [])
                    ):
                        text = span.get("text", "").strip()

                        if not text:
                            continue

                        print(
                            f"\nLine {line_number}, Span {span_number}"
                        )
                        print(f"Text: {text!r}")
                        print(f"Font: {span.get('font')}")
                        print(f"Size: {span.get('size')}")
                        print(f"Flags: {span.get('flags')}")
                        print(f"BBox: {span.get('bbox')}")

    finally:
        document.close()


if __name__ == "__main__":
    main()