
from app.db.database import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_pipeline import generate_chunk_embeddings


db = SessionLocal()

try:
    count = generate_chunk_embeddings(db)

    print(f"Generated embeddings for {count} chunks.")

finally:
    db.close()
