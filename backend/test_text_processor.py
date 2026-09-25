
from app.services.text_processor import clean_text, chunk_text


sample_text = """
John Smith is a Python developer with experience in
machine learning, FastAPI, SQL, and artificial intelligence.

He has worked on several machine learning projects involving
data preprocessing, feature engineering, model training,
and evaluation.

His projects include disease outbreak prediction using
historical healthcare datasets and an AI-powered visual
product search system.

He is also interested in building production-ready AI
applications using RAG, embeddings, vector databases,
and large language models.
"""


cleaned_text = clean_text(sample_text)

chunks = chunk_text(
    cleaned_text,
    chunk_size=200,
    chunk_overlap=40,
)

print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {i} ---")
    print(chunk)

