---
name: local-ai-terminal-app
description: Build terminal-based apps that use a local AI model (via Ollama) as the processing engine, with a menu-driven CLI UI where the model runs entirely in the background and the user only sees the app interface.
version: 1.0.0
author: Nous Research
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [terminal, cli, local-ai, ollama, typer, rich, vision-model, backend-hidden]
    category: software-development
    related_skills: [software-development]
---

# Local AI Terminal App

Build terminal-based applications that use a local AI model (via Ollama) as the processing engine, with a menu-driven CLI UI where the model runs entirely in the background and the user only sees the app interface.

## When to use
- Building a CLI/TUI app backed by a local AI model
- Any project where the user wants a clean visible interface ("app name") but all processing happens through a local model
- Projects needing image understanding, text extraction, or Q&A from uploaded files

## Architecture
1. **CLI layer**: typer + rich for the menu-driven terminal interface
2. **State layer**: JSON file in the user's home directory for session persistence
3. **Model layer**: Ollama REST API (port 11434) for the local model
4. **Image layer**: PIL for image loading and base64 encoding (no OCR tools)

## Core workflow
1. Start the Ollama server (already running on port 11434 in this environment)
2. Verify the model is loaded via `ollama list`
3. Load image through the CLI: either paste path or terminal file browser
4. Encode image to base64 data URI using PIL
5. Send image + prompt to Ollama `POST /api/chat` endpoint
6. Display the model's response
7. Save state to `~/.<app_name>/session_state.json` for follow-up questions

## Key rules
- Model name and internal details are ALWAYS hidden from the user - only show the app name ("Student Doc AI")
- No OCR/other tools - the vision model handles all image processing
- Thread-safe state management with a lock
- Image encoding: base64 + data URI prefix for Ollama API
- Preserve exact formatting in extracted text (line breaks, paragraphs)

## Backend must never be visible
```python
# User only sees "Student Doc AI" - never the model name
print("[Student Doc AI] Processing image...")

# Model is invoked via Ollama, entirely in the background
response = ollama_client.chat_completion(messages, images=[base64_encoded_image])
```

## Terminal UI patterns
- Use rich.panel for the main menu
- Use rich.table for file browsing
- Use rich.prompt for input
- Use clear status messages ("Extracting text...", "Analyzing...", "Thinking...") to show the app is working

## Project structure
```
<app_name>/
├── <app_name>/
│   ├── __init__.py
│   ├── cli.py          # typer CLI entry point with menu
│   ├── state.py        # session state management
│   ├── ollama_client.py # Ollama API wrapper
│   ├── image_handler.py # image loading + base64 encoding
│   └── prompts.py      # prompt templates
├── README.md
└── requirements.txt
```
