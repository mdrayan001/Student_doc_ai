# Student Doc AI

**Your Local Document AI Assistant** - Extract text from images and ask questions about them, all running locally on your machine using Qwen 3.5 4B model via Ollama.

## What It Does

1. **Upload an image** (scanned document, marksheet, notes, etc.)
2. **Qwen 3.5 4B analyzes the image** from top to bottom, extracting all text accurately
3. **Ask questions** about the uploaded document - the AI answers based on the extracted text
4. **Clear document** to reset and start fresh

All processing happens locally. No data leaves your computer.

## Requirements

- **Ollama**: Install from https://ollama.com
- **Qwen 3.5 4B model**: Run `ollama pull qwen3.5:4b` in terminal
- **GPU**: NVIDIA 8GB+ VRAM recommended (4GB will work but be slower)
- **Python 3.10+** with `rich`, `Pillow`, `requests` packages

## Installation

```bash
# 1. Install Ollama
# Download from https://ollama.com and install

# 2. Install the model
ollama pull qwen3.5:4b

# 3. Install Python dependencies
pip install rich Pillow requests

# 4. Run the app
python -m student_doc_ai
```

## Usage

1. **Upload Document** (`[1]`): Upload an image of your document
2. **Extract Text** (`[2]`): Instantly extract all text from the image using Qwen 3.5 4B
3. **Ask Questions** (`[2]` from main menu): Ask questions about your document
4. **Clear** (`[3]`): Clear the current document and start fresh

## Image Requirements

- **Format**: JPG, PNG, BMP, WEBP (any format supported by the model)
- **Resolution**: 1240×1755 (standard scanned marksheet) works perfectly
- **Quality**: Ensure the document is well-lit and text is readable
- **Size**: No limit on file size, will be resized automatically if too large

## Example

```
Upload: 3rd sem marksheet.jpg
Extract: "Student Name: Zeeshan Ahmed"
Ask: "What is the student name?"
Answer: "Zeeshan Ahmed"

Ask: "What subjects are in the image?"
Answer: "Data Structure, Urdu, Mathematics, etc."
```

## Troubleshooting

**Model says "no document provided"**
- Make sure you've uploaded an image first
- Extract text before asking questions

**Model is slow**
- Close other applications
- Use GPU if available
- Larger images take longer to process

**Image not recognized**
- Ensure the image is a valid JPG/PNG
- Check the file path is correct

## Privacy

All processing is done locally on your machine. No images are uploaded to any server. The Qwen 3.5 4B model runs entirely on your device.

## License

MIT
