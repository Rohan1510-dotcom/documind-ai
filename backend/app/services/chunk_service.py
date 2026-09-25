from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.text_processor import (
    clean_text,
    chunk_text,
    chunk_blocks,
)


def create_document_chunks(
    db: Session,
    document_id: int,
    text: str | None = None,
    blocks: list[dict] | None = None,
) -> int:
    """
    Create and store document chunks.

    Structured PDF blocks are preferred when available.
    Plain text is used as a fallback.

    This keeps the ingestion pipeline document-agnostic.
    """

    # ---------------------------------------------------------
    # Remove existing chunks for this document
    # ---------------------------------------------------------

    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()

    # ---------------------------------------------------------
    # Prefer structured blocks
    # ---------------------------------------------------------

    if blocks:

        structured_chunks = chunk_blocks(
            blocks=blocks,
            chunk_size=1000,
        )

        chunks = [
            chunk["content"]
            for chunk in structured_chunks
        ]

    # ---------------------------------------------------------
    # Fallback to plain-text chunking
    # ---------------------------------------------------------

    elif text:

        cleaned_text = clean_text(
            text
        )

        chunks = chunk_text(
            cleaned_text,
            chunk_size=1000,
            chunk_overlap=100,
        )

    else:

        chunks = []

    # ---------------------------------------------------------
    # Store chunks
    # ---------------------------------------------------------

    for index, chunk in enumerate(chunks):

        document_chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=chunk,
        )

        db.add(document_chunk)

    db.commit()

    return len(chunks)