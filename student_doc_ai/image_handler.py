"""Image handling for Student Doc AI.

This module handles image loading, validation, and base64 encoding.
All text extraction is done by the local Qwen 3.5 4B vision model -
no OCR or external text extraction tools are used.
"""

import base64
import io
from pathlib import Path
from PIL import Image

# Supported image formats (recognized by the vision model)
SUPPORTED_FORMATS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff", "tif", "gif"}


class ImageError(Exception):
    """Raised when image loading or processing fails."""
    pass


def is_supported_image(file_path: str | Path) -> bool:
    """Check if the file is a supported image format."""
    try:
        path = Path(file_path)
        suffix = path.suffix.lower().lstrip(".")
        return suffix in SUPPORTED_FORMATS
    except Exception:
        return False


def load_image(file_path: str | Path) -> Image.Image:
    """Load an image from the given path.

    Args:
        file_path: Path to the image file.

    Returns:
        A PIL Image object.

    Raises:
        ImageError: If the image cannot be loaded.
    """
    path = Path(file_path)
    if not path.exists():
        raise ImageError(f"Image file not found: {file_path}")

    if not is_supported_image(file_path):
        raise ImageError(f"Unsupported image format. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}")

    try:
        img = Image.open(path)
        # Verify the image is readable
        img.verify()
        # Re-open since verify() closes the file
        img = Image.open(path)
        return img
    except Exception as e:
        raise ImageError(f"Failed to load image '{file_path}': {e}")


def encode_image_to_base64(image: Image.Image) -> str:
    """Encode a PIL Image to a base64 string (without data URI prefix).

    The Ollama API expects just the base64 string, not the data URI prefix.

    Args:
        image: A PIL Image object.

    Returns:
        A base64-encoded string (without prefix).
    """
    buf = io.BytesIO()
    # Save as PNG for lossless compression
    image.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return encoded


def encode_image_file_to_base64(file_path: str | Path) -> str:
    """Load an image from file and encode to base64 data URI.

    Args:
        file_path: Path to the image file.

    Returns:
        A base64-encoded data URI string.
    """
    img = load_image(file_path)
    return encode_image_to_base64(img)


def get_image_size(file_path: str | Path) -> tuple[int, int]:
    """Get the dimensions of an image.

    Args:
        file_path: Path to the image file.

    Returns:
        A tuple of (width, height).
    """
    img = load_image(file_path)
    return img.size


def resize_image_for_model(image: Image.Image, max_width: int = 1200) -> Image.Image:
    """Resize an image to fit within the model's context window.

    Reduces image dimensions to speed up processing while maintaining
    readability. This is especially important for large images.

    The model can process images up to ~1200px wide without quality loss.
    Images smaller than 1200px are kept as-is to preserve text clarity.

    Args:
        image: PIL Image object.
        max_width: Maximum width in pixels (default: 1200).

    Returns:
        Resized PIL Image object (same as input if already within limits).
    """
    width, height = image.size

    # If image is already small enough, return as-is
    if width <= max_width:
        return image

    # Calculate new height maintaining aspect ratio
    ratio = max_width / width
    new_height = int(height * ratio)
    new_width = max_width

    # Resize with high-quality resampling
    resized = image.resize((new_width, new_height), Image.LANCZOS)
    return resized
