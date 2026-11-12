"""
Student Doc AI - Main entry point.

A terminal-based document AI assistant that uses Qwen 3.5 4B
(via Ollama) to extract text from images and answer questions
about uploaded documents.

Run with: python -m student_doc_ai
"""

if __name__ == "__main__":
    from .cli import main
    main()
