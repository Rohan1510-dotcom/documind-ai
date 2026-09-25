import fitz

PDF_PATH = r"C:\Users\Rohan Patil\Downloads\resume1.pdf"

document = fitz.open(PDF_PATH)

for page_number, page in enumerate(document, start=1):

    print(f"\n{'=' * 70}")
    print(f"PAGE {page_number}")
    print(f"{'=' * 70}")

    data = page.get_text("dict")

    for block in data["blocks"]:

        if block.get("type") != 0:
            continue

        for line in block.get("lines", []):

            for span in line.get("spans", []):

                text = span.get("text", "").strip()

                if not text:
                    continue

                print(
                    f"TEXT: {text!r}\n"
                    f"FONT: {span.get('font')}\n"
                    f"SIZE: {span.get('size')}\n"
                    f"FLAGS: {span.get('flags')}\n"
                    f"BBOX: {span.get('bbox')}\n"
                    f"{'-' * 50}"
                )

document.close()
