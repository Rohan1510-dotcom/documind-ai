
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.documents import router
from app.db.database import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.conversation import Conversation
from app.models.message import Message


# --------------------------------------------------
# Test application
# --------------------------------------------------

app = FastAPI()
app.include_router(router)

mock_db = MagicMock()


def override_get_db():
    yield mock_db


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# --------------------------------------------------
# Reset mocks before each test
# --------------------------------------------------

def setup_function():
    mock_db.reset_mock(side_effect=True, return_value=True)


# --------------------------------------------------
# Test 1: Successful document deletion
# --------------------------------------------------

def test_delete_document_success():
    document = SimpleNamespace(id=101)

    conversations = [
        SimpleNamespace(id=201),
        SimpleNamespace(id=202),
    ]

    document_query = MagicMock()
    document_query.filter.return_value.first.return_value = document

    conversation_query = MagicMock()
    conversation_query.filter.return_value.all.return_value = conversations

    mock_db.query.side_effect = [
        document_query,
        conversation_query,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    ]

    response = client.delete("/documents/101")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Document deleted successfully.",
        "document_id": 101,
    }

    mock_db.delete.assert_called_once_with(document)
    mock_db.commit.assert_called_once()

    assert mock_db.query.call_args_list[0].args[0] is Document
    assert mock_db.query.call_args_list[1].args[0] is Conversation
    assert mock_db.query.call_args_list[2].args[0] is Message
    assert mock_db.query.call_args_list[3].args[0] is Message
    assert mock_db.query.call_args_list[4].args[0] is Conversation
    assert mock_db.query.call_args_list[5].args[0] is DocumentChunk


# --------------------------------------------------
# Test 2: Document does not exist
# --------------------------------------------------

def test_delete_document_not_found():
    document_query = MagicMock()
    document_query.filter.return_value.first.return_value = None

    mock_db.query.return_value = document_query

    response = client.delete("/documents/999")

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Document not found."
    }

    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()