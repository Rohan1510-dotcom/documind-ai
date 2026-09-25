from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.question import QuestionRequest, QuestionResponse
from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/documents",
    tags=["Questions"],
)


@router.post(
    "/{document_id}/ask",
    response_model=QuestionResponse,
)
def ask_question(
    document_id: int,
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    # 1. Check that the document exists
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # 2. Check that the document is ready
    if document.status != "processed":
        raise HTTPException(
            status_code=400,
            detail="Document is not ready for questions",
        )

    # 3. Check that the conversation exists
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == request.conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # 4. Make sure the conversation belongs to this document
    if conversation.document_id != document_id:
        raise HTTPException(
            status_code=400,
            detail="Conversation does not belong to this document",
        )

    # 5. Save the user's question
    user_message = Message(
        conversation_id=request.conversation_id,
        role="user",
        content=request.question,
    )

    db.add(user_message)
    db.commit()

    # 6. Generate the answer using conversational RAG
    result = answer_question(
        db=db,
        question=request.question,
        document_id=document_id,
        conversation_id=request.conversation_id,
        top_k=6,
    )

    # 7. Save the AI's answer
    assistant_message = Message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=result["answer"],
    )

    db.add(assistant_message)
    db.commit()

    # 8. Return answer and sources
    return result