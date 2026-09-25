from app.services.document_processor import extract_blocks_from_pdf
from app.services.text_processor import chunk_blocks


PDF_PATH = "uploads/resume1.pdf"


def main():
    blocks = extract_blocks_from_pdf(PDF_PATH)

    chunks = chunk_blocks(
        blocks=blocks,
        chunk_size=1000,
    )

    print("\n" + "=" * 70)
    print("SEMANTIC CHUNKS")
    print("=" * 70)

    print(f"\nTotal chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks):

        print("\n" + "-" * 70)
        print(f"CHUNK {index}")
        print("-" * 70)

        print(chunk["content"])


if __name__ == "__main__":
    main()