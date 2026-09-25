
from app.db.database import SessionLocal
from app.models.conversation import Conversation
from app.services.rag_service import answer_question


db = SessionLocal()

try:
    document_id = 51

    conversation = (
        db.query(Conversation)
        .filter(Conversation.document_id == document_id)
        .order_by(Conversation.created_at.desc())
        .first()
    )

    if conversation is None:
        raise ValueError(
            f"No conversation found for document {document_id}. "
            "Create a conversation for this document first."
        )

    question = (
        "What machine learning experience does this candidate have?"
    )

    result = answer_question(
        db=db,
        question=question,
        document_id=document_id,
        conversation_id=conversation.id,
        top_k=3,
    )

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SOURCES")
    print("=" * 60)

    for source in result["sources"]:
        print(
            f"\nDocument: {source['document_id']}"
            f"\nChunk: {source['chunk_index']}"
            f"\nSimilarity: {source['similarity']:.4f}"
        )

finally:
    db.close()