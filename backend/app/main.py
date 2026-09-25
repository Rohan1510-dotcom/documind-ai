from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.api.documents import router as documents_router
from app.api.questions import router as questions_router
from fastapi.middleware.cors import CORSMiddleware
from app.models.conversation import Conversation
from app.models.message import Message
from app.api.conversations import router as conversations_router
from app.api.messages import router as messages_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="DocuMind AI",
    description="Intelligent Document Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(questions_router)
app.include_router(conversations_router)
app.include_router(messages_router)

@app.get("/")
def root():
    return {
        "message": "DocuMind AI API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }