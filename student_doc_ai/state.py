"""State management for Student Doc AI.

The app remembers the last uploaded image so the user can
ask follow-up questions about it. The state is saved to a
local JSON file in the user's home directory.

All state is managed internally - the user only sees the
Student Doc AI interface.
"""

import json
import os
import threading
from pathlib import Path
from datetime import datetime, timezone

# State file location
STATE_DIR = Path.home() / ".student_doc_ai"
STATE_FILE = STATE_DIR / "session_state.json"

# Lock for thread-safe state access
_state_lock = threading.Lock()

# Default initial state
DEFAULT_STATE = {
    "current_image_path": None,
    "current_image_name": None,
    "extracted_text": None,
    "uploaded_at": None,
    "image_dimensions": None,
}


def _get_default_state() -> dict:
    """Return a fresh default state dict."""
    return json.loads(json.dumps(DEFAULT_STATE))


def load_state() -> dict:
    """Load the session state from the state file.

    Returns:
        The session state dictionary.
    """
    with _state_lock:
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    state = _get_default_state()
                    state.update(data)
                    return state
            except (json.JSONDecodeError, IOError):
                pass
        return _get_default_state()


def save_state(state: dict) -> None:
    """Save the session state to the state file.

    Args:
        state: The state dictionary to save.
    """
    with _state_lock:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)


def clear_state() -> None:
    """Clear the session state.

    Removes all stored data including the state file.
    """
    state = _get_default_state()
    save_state(state)
    # Also remove the state file to ensure complete cleanup
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def get_current_image_path(state: dict | None = None) -> str | None:
    """Get the path of the currently loaded image.

    Args:
        state: Optional state dict (defaults to loaded state).

    Returns:
        The path of the current image, or None.
    """
    if state is None:
        state = load_state()
    return state.get("current_image_path")


def get_current_image_name(state: dict | None = None) -> str | None:
    """Get the name of the currently loaded image.

    Args:
        state: Optional state dict (defaults to loaded state).

    Returns:
        The name of the current image, or None.
    """
    if state is None:
        state = load_state()
    return state.get("current_image_name")


def get_extracted_text(state: dict | None = None) -> str | None:
    """Get the extracted text from the current image.

    Args:
        state: Optional state dict (defaults to loaded state).

    Returns:
        The extracted text, or None.
    """
    if state is None:
        state = load_state()
    return state.get("extracted_text")


def set_current_image(
    path: str,
    state: dict | None = None,
):
    """Set the current image path and update the state.

    Args:
        path: Path to the uploaded image.
        state: Optional state dict (defaults to loaded state).
    """
    if state is None:
        state = load_state()
    path_obj = Path(path)
    state["current_image_path"] = str(path)
    state["current_image_name"] = path_obj.name
    state["uploaded_at"] = datetime.now(timezone.utc).isoformat()
    state["image_dimensions"] = get_image_size(path)
    save_state(state)


def set_extracted_text(text: str, state: dict | None = None) -> None:
    """Set the extracted text in the state.

    Args:
        text: The extracted text.
        state: Optional state dict (defaults to loaded state).
    """
    if state is None:
        state = load_state()
    state["extracted_text"] = text
    save_state(state)


def get_uploaded_at(state: dict | None = None) -> str | None:
    """Get when the current image was uploaded.

    Args:
        state: Optional state dict (defaults to loaded state).

    Returns:
        The upload timestamp, or None.
    """
    if state is None:
        state = load_state()
    return state.get("uploaded_at")


def is_image_loaded(state: dict | None = None) -> bool:
    """Check if an image is currently loaded.

    Args:
        state: Optional state dict (defaults to loaded state).

    Returns:
        True if an image is loaded, False otherwise.
    """
    if state is None:
        state = load_state()
    return state.get("current_image_path") is not None


def get_image_dimensions() -> tuple[int, int] | None:
    """Get the dimensions of the current image.

    Returns:
        A tuple of (width, height), or None if no image is loaded.
    """
    path = get_current_image_path()
    if path:
        return get_image_size(path)
    return None


def get_image_size(file_path: str | Path) -> tuple[int, int]:
    """Get the dimensions of an image file.

    Args:
        file_path: Path to the image file.

    Returns:
        A tuple of (width, height).
    """
    from .image_handler import load_image

    img = load_image(file_path)
    return img.size
