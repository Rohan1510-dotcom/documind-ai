from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.models.conversation import Conversation


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post("/{document_id}")
def create_conversation(
    document_id: int,
    db: Session = Depends(get_db),
):
    # Check that the document exists
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # Only allow conversations for processed documents
    if document.status != "processed":
        raise HTTPException(
            status_code=400,
            detail="Document is not ready for conversations.",
        )

    conversation = Conversation(
        document_id=document_id,
        title="New Conversation",
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "id": conversation.id,
        "document_id": conversation.document_id,
        "title": conversation.title,
        "created_at": conversation.created_at,
    }