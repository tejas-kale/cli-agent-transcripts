import llm
from rich.console import Console

console = Console()

def generate_title(transcript_text: str) -> str:
    """
    Generates a concise title for the transcript using Simon Willison's llm package.
    """
    model_id = 'gemini-3-flash-preview'
    
    try:
        model = llm.get_model(model_id)
        
        prompt = (
            "Analyze the following conversation transcript and generate a short, "
            "descriptive file-name friendly title (max 5-8 words). "
            "Do not use special characters or path separators. "
            "Return ONLY the title text, nothing else.\n\n"
            f"Transcript Start:\n{transcript_text[:10000]}"
        )

        response = model.prompt(prompt)
        title = response.text().strip()
        
        # Cleanup
        return title.replace("/", "-").replace("\\", "-").replace(":", "").replace("\"", "").replace("'", "")
    except llm.UnknownModelError:
        console.print(f"[yellow]Warning: Model '{model_id}' is not available. Ensure llm-gemini is installed and configured.[/yellow]")
        return None
    except Exception as e:
        console.print(f"[yellow]Warning: Failed to generate title with LLM: {e}[/yellow]")
        return None

