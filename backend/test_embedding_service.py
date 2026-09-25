
from app.services.embedding_service import generate_embedding


text = "Python developer with machine learning experience"

embedding = generate_embedding(text)

print("Embedding dimensions:", len(embedding))
print("First 10 values:", embedding[:10])
print("Embedding type:", type(embedding))

