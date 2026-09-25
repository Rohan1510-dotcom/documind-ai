
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.documents import router
from app.db.database import get_db


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
    mock_db.reset_mock()


# --------------------------------------------------
# Test 1: Successful PDF upload
# --------------------------------------------------

@patch("app.api.documents.generate_chunk_embeddings")
@patch("app.api.documents.create_document_chunks")
@patch("app.api.documents.extract_blocks_from_pdf")
@patch("app.api.documents.save_uploaded_file")
def test_upload_pdf_success(
    mock_save,
    mock_extract,
    mock_create_chunks,
    mock_generate_embeddings,
):
    mock_save.return_value = "uploads/test.pdf"

    mock_extract.return_value = [
        {"text": "Sample resume content"}
    ]

    def refresh_document(document):
        document.id = 101

    mock_db.refresh.side_effect = refresh_document

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Document processed successfully"
    assert data["document_id"] == 101
    assert data["filename"] == "test.pdf"
    assert data["status"] == "processed"
    assert data["extracted_characters"] == len(
        "Sample resume content"
    )

    mock_save.assert_called_once()
    mock_extract.assert_called_once_with("uploads/test.pdf")
    mock_create_chunks.assert_called_once()
    mock_generate_embeddings.assert_called_once()

    mock_db.add.assert_called_once()
    assert mock_db.commit.call_count == 2


# --------------------------------------------------
# Test 2: Reject non-PDF uploads
# --------------------------------------------------

def test_upload_rejects_non_pdf():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test.txt",
                b"plain text content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Only PDF files are supported."
    }

    mock_db.add.assert_not_called()


# --------------------------------------------------
# Test 3: Handle PDF processing failure
# --------------------------------------------------

@patch("app.api.documents.generate_chunk_embeddings")
@patch("app.api.documents.create_document_chunks")
@patch("app.api.documents.extract_blocks_from_pdf")
@patch("app.api.documents.save_uploaded_file")
def test_upload_processing_failure(
    mock_save,
    mock_extract,
    mock_create_chunks,
    mock_generate_embeddings,
):
    mock_save.return_value = "uploads/broken.pdf"

    mock_extract.side_effect = Exception(
        "PDF extraction failed"
    )

    def refresh_document(document):
        document.id = 102

    mock_db.refresh.side_effect = refresh_document

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "broken.pdf",
                b"fake pdf content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Document processing failed. Please try again."
        )
    }

    mock_create_chunks.assert_not_called()
    mock_generate_embeddings.assert_not_called()

    # The document should be marked as failed.
    document = mock_db.add.call_args.args[0]

    assert document.status == "failed"
    assert document.error_message == "PDF extraction failed"

    # Initial commit and failure-state commit.
    assert mock_db.commit.call_count == 2