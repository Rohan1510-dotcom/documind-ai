from app.services.document_processor import extract_blocks_from_pdf
from app.services.structure_service import classify_document_blocks


PDF_PATH = "uploads/resume1.pdf"


def main():
    blocks = extract_blocks_from_pdf(PDF_PATH)

    classified_blocks = classify_document_blocks(blocks)

    print("\n" + "=" * 70)
    print("STRUCTURE DETECTION")
    print("=" * 70)

    for block in classified_blocks:
        print(
            f"\nBlock {block['block_number']}"
            f"\nType: {block['type']}"
            f"\nConfidence: {block['confidence']}"
            f"\nText: {block['text'][:150]!r}"
        )


if __name__ == "__main__":
    main()