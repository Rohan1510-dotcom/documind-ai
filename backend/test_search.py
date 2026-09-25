from app.db.database import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.search_service import semantic_search


db = SessionLocal()

try:
    question = "What machine learning experience does this candidate have?"

    results = semantic_search(
        db=db,
        query=question,
        limit=5,
        document_id=14,
    )

    print("\n===== RETRIEVED CHUNKS =====\n")

    for result in results:
        print(
            f"Document: {result['document_id']}"
        )
        print(
            f"Chunk: {result['chunk_index']}"
        )
        print(
            f"Similarity: {result['similarity']:.4f}"
        )
        print("\nContent:")
        print(result["content"])
        print("\n" + "=" * 80)

finally:
    db.close()