"""Ollama API client for communicating with the local Qwen 3.5 4B model.

All requests go to the local Ollama server running on port 11434.
The model is invoked entirely in the background - the user never sees
the model name or any internal details.
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

# Ollama server configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost")
OLLAMA_PORT = int(os.environ.get("OLLAMA_PORT", "11434"))
OLLAMA_BASE_URL = f"{OLLAMA_HOST}:{OLLAMA_PORT}"

# The model name is completely hidden from the user.
# The user only sees "Student Doc AI".
MODEL_NAME = os.environ.get("STUDENT_DOC_AI_MODEL", "qwen3-vl:4b-instruct")

# Timeout for model requests (in seconds)
REQUEST_TIMEOUT = 600  # 10 minutes for model inference


class OllamaError(Exception):
    """Raised when the Ollama API call fails."""
    pass


def check_ollama_available() -> bool:
    """Check if the Ollama server is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def list_available_models():
    """Return a list of model names available on the Ollama server."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [m["name"] for m in data.get("models", [])]
    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not fetch model list: {e}")
        return []


def is_model_loaded(model_name: str = MODEL_NAME) -> bool:
    """Check if the specific model is loaded in Ollama."""
    models = list_available_models()
    return model_name in models


def chat_completion(
    messages: list[dict],
    images: list[str] | None = None,
    stream: bool = False,
    **kwargs,
):
    """Send a chat completion request to the Ollama server.

    For vision models (like qwen3-vl), images are attached to the
    user message content as base64-encoded data.

    Args:
        messages: List of message dicts (role + content).
        images: List of base64-encoded image strings (with data URI prefix).
        stream: Whether to stream the response.
        **kwargs: Additional parameters passed to the API.

    Returns:
        The parsed JSON response from the API.

    Raises:
        OllamaError: If the API call fails.
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": stream,
        **kwargs,
    }

    # Attach images to the last user message (required format for vision models)
    if images:
        # Ensure the last message has an 'images' field
        if messages and messages[-1].get("role") == "user":
            if "images" not in messages[-1]:
                messages[-1]["images"] = []
            messages[-1]["images"].extend(images)
            payload["images"] = images  # Also include at top level for compatibility

    logger.info(f"Sending request to Ollama (model={MODEL_NAME})")
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out")
        raise OllamaError("Model request timed out. The model is still loading or the image is too large.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API error: {e}")
        raise OllamaError(f"Failed to communicate with the local AI model: {e}")


def generate(
    prompt: str,
    images: list[str] | None = None,
    **kwargs,
):
    """Send a generate request to the Ollama server (alternate endpoint).

    This is a convenience function for single-prompt completions.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        **kwargs,
    }
    if images:
        payload["images"] = images

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama generate error: {e}")
        raise OllamaError(f"Failed to communicate with the local AI model: {e}")
