# Student Doc AI

A terminal-based document AI assistant that uses **Qwen 3.5 4B** (running locally via Ollama) to extract text from images and answer questions about uploaded documents.

## Features

- **Local AI Processing** - All processing happens on your machine. No data leaves your device.
- **Image Upload** - Paste a file path or browse images in the terminal
- **Text Extraction** - Extract all text from document images using Qwen 3.5 4B
- **Question Answering** - Ask questions about your uploaded documents
- **No OCR Dependencies** - Everything is done by the vision-capable Qwen 3.5 4B model

## How It Works

```
┌─────────────────────────────────────┐
│       Student Doc AI (Terminal UI)   │
│                                     │
│  [1] Upload & Extract Text          │
│  [2] Ask a Question                 │
│  [3] Clear Current Document         │
│  [4] Exit                           │
│                                     │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Local Model (Qwen 3.5 4B)      │
│   Running via Ollama (local)        │
│                                     │
│  • Image analysis                   │
│  • Text extraction                  │
│  • Q&A on document content          │
└─────────────────────────────────────┘
```

## Quick Start

### 1. Install Ollama

Download and install Ollama from: https://ollama.com/download

### 2. Start Ollama

Open a terminal and run:

```bash
ollama serve
```

### 3. Download the Model

```bash
ollama pull qwen3.5:4b
```

### 4. Install Project Dependencies

```bash
pip install rich requests Pillow
```

### 5. Run Student Doc AI

```bash
python -m student_doc_ai
```

## Usage

1. **Upload a document** - Choose [1] and paste a path (e.g., `C:\Users\user\Documents\notes.png`)
2. **Extract text** - The model analyzes the image and extracts all text
3. **Ask questions** - Choose [2] and ask anything about the document
4. **Extract another document** - Choose [3] to clear the current one

## Project Structure

```
student-doc-ai/
├── student_doc_ai/
│   ├── __init__.py           # Package init
│   ├── __main__.py           # Module entry point
│   ├── cli.py                # Terminal interface
│   ├── ollama_client.py      # Local model API wrapper
│   ├── image_handler.py      # Image loading/encoding utilities
│   ├── prompts.py            # AI prompt templates
│   └── state.py              # Session state management
├── requirements.txt          # Python dependencies
└── README.md
```

## Technical Details

- **Model**: Qwen 3.5 4B (vision-capable)
- **Inference Engine**: Ollama (local)
- **Python**: 3.9+
- **UI Library**: Rich (terminal formatting)

## Privacy

All processing is done locally. Your documents and the AI model run on your machine. No images or text are sent to any external service.

## Need Help?

If Ollama is not running, the app will show an error message with setup instructions.
