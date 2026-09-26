
import math
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Locate backend/.env explicitly.
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

API_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    f"{MODEL_NAME}/pipeline/feature-extraction"
)

EMBEDDING_DIMENSION = 384


def generate_embedding(text: str) -> list[float]:
    """Generate a normalized 384-dimensional embedding."""

    # Load the token at function call time.
    load_dotenv(dotenv_path=ENV_PATH, override=False)
    hf_token = os.getenv("HF_TOKEN")

    if not hf_token:
        raise RuntimeError(
            f"HF_TOKEN is not configured. Checked: {ENV_PATH}"
        )

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": text,
            "options": {"wait_for_model": True},
        },
        timeout=60,
    )

    response.raise_for_status()
    result = response.json()

    # Handle a singleton batch: [[384 values]]
    if (
        isinstance(result, list)
        and len(result) == 1
        and isinstance(result[0], list)
        and len(result[0]) == EMBEDDING_DIMENSION
    ):
        result = result[0]

    if (
        not isinstance(result, list)
        or len(result) != EMBEDDING_DIMENSION
        or not all(
            isinstance(value, (int, float))
            for value in result
        )
    ):
        raise RuntimeError(
            "Unexpected embedding response. "
            f"Expected {EMBEDDING_DIMENSION} dimensions."
        )

    embedding = [float(value) for value in result]

    norm = math.sqrt(sum(value * value for value in embedding))

    if norm == 0:
        raise RuntimeError("Received a zero-length embedding.")

    return [value / norm for value in embedding]