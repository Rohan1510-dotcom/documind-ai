
from app.services.llm_service import generate_response


prompt = "Explain Retrieval-Augmented Generation in two simple sentences."

response = generate_response(prompt)

print("\nLLM Response:")
print(response)

