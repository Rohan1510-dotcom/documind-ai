
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables from backend/.env
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL_NAME = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
)


def generate_response(prompt: str) -> str:
    """Send a prompt to Groq and return the generated response."""

    load_dotenv(dotenv_path=ENV_PATH, override=False)
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            f"GROQ_API_KEY is not configured. Checked: {ENV_PATH}"
        )

    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2048,
            },
            timeout=120,
        )

        if not response.ok:
            raise RuntimeError(
                f"Groq API error ({response.status_code}): "
                f"{response.text}"
            )

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if not answer:
            raise RuntimeError("Groq returned an empty response.")

        return answer

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to connect to Groq API: {exc}"
        ) from exc