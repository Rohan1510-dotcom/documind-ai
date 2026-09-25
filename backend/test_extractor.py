from app.services.document_processor import extract_blocks_from_pdf

blocks = extract_blocks_from_pdf("uploads/resume1.pdf")

for i, block in enumerate(blocks):
    print("\n" + "=" * 70)
    print(f"BLOCK {i}")
    print("=" * 70)

    print("TEXT:", block["text"])
    print("PAGE:", block["page"])
    print("FONTS:", block["fonts"])
    print("FONT SIZES:", block["font_sizes"])
    print("IS BOLD:", block["is_bold"])