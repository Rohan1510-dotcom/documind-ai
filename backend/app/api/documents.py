from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.document_processor import extract_blocks_from_pdf
from app.services.document_service import save_uploaded_file
from app.services.chunk_service import create_document_chunks
from app.services.embedding_pipeline import generate_chunk_embeddings


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1. Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # 2. Save uploaded file
    file_path = save_uploaded_file(file)

    # 3. Create document record
    document = Document(
        filename=file.filename,
        file_type=file.content_type,
        status="processing",
        error_message=None,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        # 4. Extract structured PDF blocks
        blocks = extract_blocks_from_pdf(file_path)

        # 5. Reconstruct complete text
        extracted_text = "\n\n".join(
            block["text"]
            for block in blocks
        )

        document.extracted_text = extracted_text

        # 6. Create chunks
        create_document_chunks(
            db=db,
            document_id=document.id,
            blocks=blocks,
        )

        # 7. Generate embeddings
        generate_chunk_embeddings(
            db=db,
            document_id=document.id,
        )

        # 8. Mark document as successfully processed
        document.status = "processed"
        document.error_message = None

        db.commit()
        db.refresh(document)

    except Exception as error:
        # Remove partially created chunks
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete()

        # Store the actual internal error in the database
        document.status = "failed"
        document.error_message = str(error)

        db.commit()
        db.refresh(document)

        # Return a safe error message to the client
        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Please try again.",
        )

    return {
        "message": "Document processed successfully",
        "document_id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "status": document.status,
        "file_path": file_path,
        "extracted_characters": len(extracted_text),
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    # Find document
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

    # Find conversations belonging to the document
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.document_id == document_id
        )
        .all()
    )

    # Delete messages first
    for conversation in conversations:
        db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).delete()

    # Delete conversations
    db.query(Conversation).filter(
        Conversation.document_id == document_id
    ).delete()

    # Delete document chunks
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()

    # Delete document
    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
    }