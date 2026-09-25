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

                lines = block.get("lines", [])

                if len(lines) < 2:
                    continue

                print("\n" + "=" * 70)
                print(f"PAGE: {page_number}")
                print(f"PDF BLOCK: {block_number}")
                print("=" * 70)

                for line_number, line in enumerate(lines):
                    spans = [
                        span
                        for span in line.get("spans", [])
                        if span.get("text", "").strip()
                    ]

                    if not spans:
                        continue

                    text = " ".join(
                        span["text"].strip()
                        for span in spans
                    )

                    sizes = [
                        round(span.get("size", 0), 2)
                        for span in spans
                    ]

                    fonts = [
                        span.get("font", "")
                        for span in spans
                    ]

                    print(
                        f"\nLine {line_number}"
                        f"\n  Text: {text!r}"
                        f"\n  Font sizes: {sizes}"
                        f"\n  Fonts: {fonts}"
                    )

    finally:
        document.close()


if __name__ == "__main__":
    main()