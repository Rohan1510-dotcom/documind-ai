from datetime import datetime

from pydantic import BaseModel


class ConversationResponse(BaseModel):
    id: int
    document_id: int
    title: str
    created_at: datetime