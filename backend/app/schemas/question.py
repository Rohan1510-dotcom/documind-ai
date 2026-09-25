from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the document",
    )

    conversation_id: int = Field(
        ...,
        description="Conversation ID",
    )


class SourceResponse(BaseModel):
    document_id: int
    chunk_index: int
    similarity: float
    content: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]