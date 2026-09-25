import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:0.6b"


def generate_response(prompt: str) -> str:
    """
    Send a prompt to the local Ollama model
    and return the generated response.
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
            "think": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]