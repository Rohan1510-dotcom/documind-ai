from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


def generate_chunk_embeddings(
    db: Session,
    document_id: int | None = None,
) -> int:
    query = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.embedding.is_(None))
    )

    if document_id is not None:
        query = query.filter(
            DocumentChunk.document_id == document_id
        )

    chunks = (
        query
        .order_by(
            DocumentChunk.document_id,
            DocumentChunk.chunk_index,
        )
        .all()
    )

    processed_count = 0

    for chunk in chunks:
        embedding = generate_embedding(chunk.content)
        chunk.embedding = embedding
        processed_count += 1

    db.commit()

    return processed_count