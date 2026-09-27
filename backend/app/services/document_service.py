
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


# Vercel allows temporary file writes inside /tmp.
UPLOAD_DIR = Path("/tmp/documind_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(file: UploadFile) -> str:
    # Generate a unique filename to avoid collisions and unsafe paths.
    original_name = Path(file.filename or "document.pdf").name
    suffix = Path(original_name).suffix or ".pdf"
    file_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"

    with open(file_path, "wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            buffer.write(chunk)

    return str(file_path)