"""Student Doc AI - CLI Interface."""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.text import Text

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .ollama_client import (
    chat_completion,
    check_ollama_available,
    is_model_loaded,
    OllamaError,
)
from .image_handler import (
    load_image,
    encode_image_to_base64,
    is_supported_image,
    resize_image_for_model,
)
from .state import (
    load_state,
    save_state,
    get_current_image_path,
    get_current_image_name,
    get_extracted_text,
    set_current_image,
    set_extracted_text,
    is_image_loaded,
    clear_state,
)
from . import prompts as PROMPTS
from . import __version__

console = Console()
BRAND_NAME = "Student Doc AI"
BRAND_TAGLINE = "Your Local Document AI Assistant"
BRAND_VERSION = "v1.0.0"

ANALYSIS_MESSAGES = [
    "Analyzing document...",
    "Extracting text...",
    "Processing image...",
    "Reading content...",
    "Studying document...",
]


class StudentDocAI:
    """Main application class for Student Doc AI."""

    def __init__(self):
        self.state = load_state()
        self.current_image_encoded = None
        self.current_image_extracted = False
        self.current_image_path = None

    def show_brand(self):
        header_text = Text()
        header_text.append(f" {BRAND_NAME} ", style="bold cyan")
        header_text.append(f" v{BRAND_VERSION} ", style="bold green")
        header_text.append("  ", style="dim")
        header_text.append(BRAND_TAGLINE, style="dim")

        console.print()
        console.print(
            Panel(
                header_text,
                border_style="bright_cyan",
                padding=(0, 2),
            )
        )
        console.print()

    def show_main_menu(self):
        self.show_brand()
        console.print("  [1] Upload & Extract Text", style="bold")
        console.print("  [2] Ask a Question", style="bold")
        console.print("  [3] View Extracted Text", style="bold")
        console.print("  [4] Clear Current Document", style="bold")
        console.print("  [5] Exit", style="bold")
        console.print()
        choice = IntPrompt.ask("  Select an option [1/2/3/4/5]", choices=["1", "2", "3", "4", "5"])
        if choice == 1:
            self.upload_and_extract()
        elif choice == 2:
            self.ask_question()
        elif choice == 3:
            self.show_extracted_text()
        elif choice == 4:
            self.clear_document()
        elif choice == 5:
            self.exit_app()

    def upload_and_extract(self):
        console.print("\n[bold cyan]Step 1: Upload Image[/bold cyan]")
        console.print("  [1] Paste image file path")
        choice = IntPrompt.ask("  Select upload method [1/2]", choices=["1"])
        if choice == 1:
            self.paste_path_upload()
        else:
            self.browse_upload()

    def paste_path_upload(self):
        console.print("\n[bold cyan]Paste a full file path[/bold cyan]")
        console.print("  e.g. C:\\Users\\user\\Documents\\notes.png")
        path = Prompt.ask("  Image path", default="")
        if not path:
            console.print("[dim]No path entered. Going back to main menu.[/dim]")
            return
        try:
            if not is_supported_image(path):
                console.print(f"[bold red]Error:[/bold red] Unsupported format.")
                return
            if not Path(path).is_file():
                console.print(f"[bold red]Error:[/bold red] File not found: {path}")
                return
            img = load_image(path)
            img = resize_image_for_model(img)
            self.current_image_encoded = encode_image_to_base64(img)
            console.print("[green]✓[/green] Image encoded successfully")
            set_current_image(path)
            self.current_image_extracted = False
            console.print("\n[bold cyan]Step 2: Text Extraction[/bold cyan]")
            choice = IntPrompt.ask("  Select [1/2]", choices=["1", "2"])
            if choice == 1:
                self.process_image(path)
            else:
                self.show_extracted_text(None)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

    def browse_upload(self):
        console.print("\n[bold cyan]Terminal File Browser[/bold cyan]")
        file_path = self._browse_loop()
        if not file_path:
            return
        try:
            img = load_image(file_path)
            img = resize_image_for_model(img)
            self.current_image_encoded = encode_image_to_base64(img)
            set_current_image(file_path)
            self.current_image_extracted = False
            console.print("\n[bold cyan]Step 2: Text Extraction[/bold cyan]")
            choice = IntPrompt.ask("  Select [1/2]", choices=["1", "2"])
            if choice == 1:
                self.process_image(file_path)
            else:
                self.show_extracted_text(None)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

    def _browse_loop(self):
        current_dir = Path.cwd()
        while True:
            console.print(f"\n[bold]Current directory:[/bold] {current_dir}")
            items = []
            for item in sorted(current_dir.iterdir()):
                if item.name.startswith("."):
                    continue
                if item.is_dir():
                    items.append((str(item.resolve()), f"[DIR]  {item.name}/"))
                elif is_supported_image(str(item)):
                    items.append((str(item.resolve()), f"[IMG] {item.name}"))
            if not items:
                console.print("[dim]No files found.[/dim]\n")
                choice = IntPrompt.ask("  Select", choices=["1", "2", "3"])
                if choice == 1:
                    new_dir = Prompt.ask("  Enter directory path", default=str(current_dir))
                    p = Path(new_dir)
                    if p.exists() and p.is_dir():
                        current_dir = p
                    else:
                        console.print("[red]Directory not found.[/red]")
                    continue
                elif choice == 2:
                    current_dir = current_dir.parent
                    continue
                elif choice == 3:
                    return None
            for i, (path, label) in enumerate(items, 1):
                console.print(f"  [{i}] {label}")
            console.print(f"  [{len(items)+1}] Change directory")
            console.print(f"  [{len(items)+2}] Go back to parent directory")
            console.print(f"  [{len(items)+3}] Cancel")
            choice = IntPrompt.ask("  Select", choices=[str(i) for i in range(1, len(items)+4)])
            if choice <= len(items):
                return items[choice - 1][0]
            elif choice == len(items) + 1:
                new_dir = Prompt.ask("  Enter directory path", default=str(current_dir))
                p = Path(new_dir)
                if p.exists() and p.is_dir():
                    current_dir = p
                else:
                    console.print("[red]Directory not found.[/red]")
            elif choice == len(items) + 2:
                current_dir = current_dir.parent
            elif choice == len(items) + 3:
                return None

    def process_image(self, image_path: str):
        console.print(f"\n[bold cyan]Uploading and analyzing: {Path(image_path).name}[/bold cyan]")
        try:
            img = load_image(image_path)
            img = resize_image_for_model(img)
            self.current_image_encoded = encode_image_to_base64(img)
            console.print("[green]✓[/green] Image encoded successfully")
        except Exception as e:
            console.print(f"[bold red]Error encoding image:[/bold red] {e}")
            self.current_image_encoded = None
            return

        set_current_image(image_path)
        self.current_image_extracted = True

        console.print(f"[dim]{ANALYSIS_MESSAGES[0]}[/dim]")
        try:
            messages = [
                {
                    "role": "user",
                    "content": "Extract ALL text from this image. Provide the complete, accurate text content. Do not add any comments or explanations - only the extracted text.",
                }
            ]
            response = chat_completion(messages, images=[self.current_image_encoded])
            extracted_text = response.get("message", {}).get("content", "No text extracted.")
            extracted_text = extracted_text.strip()
            if not extracted_text:
                extracted_text = "No text could be extracted from this image."
            set_extracted_text(extracted_text)
            self.current_image_extracted = True
            self.current_image_path = image_path
            console.print("\n[bold green]✓[/bold green] Text extraction complete!")
            console.print("[bold]Extracted text is now ready.[/bold]")
            console.print("  [1] View extracted text")
            console.print("  [2] Extract another document")
            console.print("  [3] Go to main menu")
            console.print()
            choice = IntPrompt.ask("  Select", choices=["1", "2", "3"])
            if choice == 1:
                self.show_extracted_text()
            elif choice == 2:
                self.upload_and_extract()
            elif choice == 3:
                self.show_main_menu()
        except OllamaError as e:
            console.print(f"[bold red]Model error:[/bold red] {e}")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

    def ask_question(self):
        if not is_image_loaded():
            console.print("[bold yellow]No document loaded. Please upload a document first.[/bold yellow]")
            self.show_main_menu()
            return
        path = get_current_image_path()
        image_name = get_current_image_name()
        console.print(f"\n[bold cyan]Asking a question about: {image_name}[/bold cyan]")
        question = Prompt.ask("  Question")
        if not question.strip():
            self.show_main_menu()
            return
        if not self.current_image_encoded:
            try:
                self.current_image_encoded = encode_image_file_to_base64(path)
            except Exception as e:
                console.print(f"[bold red]Error loading document:[/bold red] {e}")
                return

        # Get the extracted text to provide context
        extracted_text = get_extracted_text()
        if not extracted_text or extracted_text == "No text could be extracted":
            console.print(f"[dim]Re-analyzing document to answer your question...[/dim]")
            try:
                messages = [
                    {
                        "role": "user",
                        "content": "Extract ALL text from this image. Provide the complete, accurate text content. Do not add any comments or explanations - only the extracted text.",
                    }
                ]
                response = chat_completion(messages, images=[self.current_image_encoded])
                extracted_text = response.get("message", {}).get("content", "").strip()
                if not extracted_text:
                    extracted_text = "No text could be extracted from this image."
                set_extracted_text(extracted_text)
            except Exception as e:
                console.print(f"[bold red]Error analyzing document:[/bold red] {e}")
                self.show_main_menu()
                return

        console.print(f"[dim]Thinking about your question...[/dim]")

        try:
            # Build the question-answering prompt with extracted text context
            messages = [
                {
                    "role": "user",
                    "content": f"""Answer this question about the document below.

EXTRACTED TEXT:
{extracted_text}

---
Question: {question}
Based on the EXTRACTED TEXT above, provide a clear and accurate answer. Do not make up information that is not in the text. If the text does not contain the answer, say you cannot find the answer in the document.""",
                }
            ]

            response = chat_completion(messages, images=[self.current_image_encoded])
            answer = response.get("message", {}).get("content", "I couldn't generate an answer.")

            console.print("\n[bold green]Answer:[/bold green]")
            console.print("-" * 50)
            console.print(answer)
            console.print("-" * 50)

            console.print("\n[bold]Ask another question?[/bold]")
            console.print("  [1] Ask another question?")
            console.print("  [2] Go to main menu")
            console.print()
            choice = IntPrompt.ask("  Select [1/2]", choices=["1", "2"])
            if choice == 1:
                self.ask_question()
            elif choice == 2:
                self.show_main_menu()
        except OllamaError as e:
            console.print(f"[bold red]Model error:[/bold red] {e}")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

    def show_extracted_text(self):
        extracted_text = get_extracted_text() or "No text extracted from document."
        console.print("\n[bold]Extracted Text from Document:[/bold]")
        console.print("=" * 60)
        console.print(Panel(
            extracted_text,
            border_style="green",
            padding=(1, 2),
            width=100,
        ))
        console.print("=" * 60)
        console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
        console.print("  [1] Ask a question about the document", style="bold")
        console.print("  [2] Extract another document", style="bold")
        console.print("  [3] Go to main menu", style="bold")
        choice = IntPrompt.ask("  Select", choices=["1", "2", "3"])
        if choice == 1:
            self.ask_question()
        elif choice == 2:
            self.upload_and_extract()
        elif choice == 3:
            self.show_main_menu()

    def clear_document(self):
        console.print("[bold cyan]Clearing current document...[/bold cyan]")
        clear_state()
        self.current_image_encoded = None
        self.current_image_extracted = False
        console.print("[green]✓[/green] Document cleared.")
        self.show_main_menu()

    def exit_app(self):
        console.print("\n[bold cyan]Thank you for using Student Doc AI![/bold cyan]")
        console.print("[dim]All processing was done locally on your device.[/dim]")
        sys.exit(0)

    def run(self):
        console.print("\n" + "=" * 60)
        console.print(f"  [bold cyan]{BRAND_NAME}[/bold cyan]  [dim]{BRAND_TAGLINE}[/dim]")
        console.print(f"  [dim]Version: v1.0.0[/dim]")
        console.print("=" * 60)
        if not check_ollama_available():
            console.print("[bold red]Error:[/bold red] Cannot connect to local Ollama server.")
            console.print("Please make sure Ollama is installed and running.")
            sys.exit(1)
        if not is_model_loaded():
            console.print("[bold red]Error:[/bold red] The Qwen 3.5 4B model is not loaded.")
            sys.exit(1)
        console.print("[green]✓[/green] Student Doc AI is ready")
        console.print("[dim]All processing done locally on your device[/dim]")
        while True:
            self.show_main_menu()


def main():
    app = StudentDocAI()
    app.run()


if __name__ == "__main__":
    main()
