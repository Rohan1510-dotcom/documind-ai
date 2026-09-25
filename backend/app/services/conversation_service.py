from sqlalchemy.orm import Session

from app.models.message import Message


def get_conversation_messages(
    db: Session,
    conversation_id: int,
) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )