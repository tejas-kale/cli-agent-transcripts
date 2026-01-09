import typer
import json
import re
from pathlib import Path
from rich.console import Console
from rich.progress import track
from .parsers import TranscriptParser
from .html_formatter import format_gemini_html, format_claude_html
from .formatter import format_timestamp, extract_title
from .ai import generate_title

app = typer.Typer(help="Tool to save Gemini and Claude transcripts to HTML.")
console = Console()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove illegal characters but keep spaces and casing."""
    return re.sub(r'[\\/*?:\"<>|]', "", filename)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    output_dir: Path = typer.Option(
        Path("transcripts"), 
        "--output-dir", "-o", 
        help="Directory to save the transcripts."
    ),
    source: str = typer.Option(
        "all", 
        "--source", "-s", 
        help="Source of transcripts: 'gemini', 'claude', or 'all'."
    )
):
    """
    Interactively select and save transcripts from Gemini CLI and Claude Code to single HTML files.
    """
    if ctx.invoked_subcommand is not None:
        return

    parser = TranscriptParser()
    
    with console.status("[bold green]Scanning for transcripts..."):
        transcripts = list(parser.get_all_transcripts(source))
    
    if not transcripts:
        console.print("[yellow]No transcripts found.[/yellow]")
        return

    # Pre-process for display and sorting
    display_items = []
    for t in transcripts:
        t_id = "unknown"
        t_date_str = ""
        
        if t['source'] == 'gemini':
            t_id = t['data'].get('sessionId')
            t_date_str = t['data'].get('startTime', '')
        elif t['source'] == 'claude':
            t_id = t['id']
            if t['messages']:
                t_date_str = t['messages'][0].get('timestamp', '')
        
        formatted_date = format_timestamp(t_date_str)
        title = extract_title(t)
        
        display_label = f"[{t['source'].upper()}] {formatted_date} - {title}"
        
        display_items.append({
            "name": display_label,
            "value": t,
            "sort_key": t_date_str or "" # Use raw ISO string for sorting
        })
    
    # Sort by date (descending, newest first)
    display_items.sort(key=lambda x: x["sort_key"], reverse=True)
    
    # Slice top 10
    top_items = display_items[:10]

    # Render List
    console.print("\n[bold]Latest Transcripts:[/bold]")
    for idx, item in enumerate(top_items, 1):
        console.print(f"[bold cyan]{idx}.[/bold cyan] {item['name']}")
    
    console.print("\n[dim]Enter the numbers of the transcripts to save (e.g. '1 3'), 'all' for these 10, or 'q' to quit.[/dim]")

    # Simple, robust input loop
    selected_transcripts = []
    while True:
        selection = typer.prompt("Select").strip().lower()
        
        if selection == 'q':
            console.print("[yellow]Exiting.[/yellow]")
            return
        
        if selection == 'all':
            selected_transcripts = [item['value'] for item in top_items]
            break
            
        # Parse numbers
        try:
            indices = [int(s) for s in selection.replace(',', ' ').split()]
            valid_indices = [i for i in indices if 1 <= i <= len(top_items)]
            
            if not valid_indices:
                console.print("[red]No valid numbers selected. Try again.[/red]")
                continue
                
            selected_transcripts = [top_items[i-1]['value'] for i in valid_indices]
            break
        except ValueError:
            console.print("[red]Invalid input. Please enter numbers, 'all', or 'q'.[/red]")

    output_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"Saving [bold]{len(selected_transcripts)}[/bold] transcripts to [bold]{output_dir}[/bold]...")

    for transcript in track(selected_transcripts, description="Processing & Generating Titles..."):
        try:
            # Prepare content for title generation
            raw_text = ""
            if transcript['source'] == 'gemini':
                raw_text = json.dumps(transcript['data'].get('messages', []), indent=2)
            elif transcript['source'] == 'claude':
                raw_text = json.dumps(transcript.get('messages', []), indent=2)

            # Generate Title using Gemini API
            ai_title = generate_title(raw_text)
            
            # Formatter and Filename Logic
            content = ""
            filename = ""
            
            if transcript['source'] == 'gemini':
                session_id = transcript['data'].get('sessionId')
                content = format_gemini_html(transcript['data'], title=ai_title)
                
                if ai_title:
                     filename = f"{sanitize_filename(ai_title)}.html"
                else:
                     filename = f"gemini-{session_id}.html"

            elif transcript['source'] == 'claude':
                session_id = transcript['id']
                content = format_claude_html(session_id, transcript['messages'], title=ai_title)
                
                if ai_title:
                     filename = f"{sanitize_filename(ai_title)}.html"
                else:
                     filename = f"claude-{session_id}.html"
            else:
                continue

            output_path = output_dir / filename
            output_path.write_text(content, encoding='utf-8')
            
        except Exception as e:
            console.print(f"[red]Failed to save {transcript.get('path')}: {e}[/red]")

    console.print("[green]Done![/green]")

if __name__ == "__main__":
    app()