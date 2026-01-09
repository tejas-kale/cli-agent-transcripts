# Project: cc-transcripts

## Overview

`cc-transcripts` is a Python CLI tool designed to export conversation history from **Gemini CLI** and **Claude Code** local sessions into self-contained, readable HTML files.

Although the project metadata mentions Markdown export, the current implementation generates HTML files with embedded CSS and JavaScript to support features like collapsible tool execution details and clean message formatting.

### Key Features
-   **Source Support**: Scans local directories for Gemini (`.gemini/tmp/...`) and Claude (`.claude/projects/...`) session files.
-   **Interactive Selection**: Lists the 10 latest sessions for the user to choose from.
-   **AI-Powered Titles**: Uses the `llm` library (specifically `gemini-3-flash-preview`) to generate concise titles for transcripts based on their content.
-   **Rich Output**: Produces HTML files with syntax highlighting for code and structured viewing for JSON tool outputs.

## Architecture

*   **Entry Point**: `src/cc_transcripts/main.py` defined as the `cc-transcripts` script.
*   **CLI Framework**: `typer` handles command-line arguments and interactivity.
*   **UI/Display**: `rich` is used for terminal output, status spinners, and progress bars.
*   **Parsing**: `src/cc_transcripts/parsers.py` contains logic to locate and read JSON/JSONL logs from specific system paths.
*   **Formatting**: `src/cc_transcripts/html_formatter.py` converts the parsed data into HTML, using `markdown` for text content and custom HTML templates for structure.
*   **AI Integration**: `src/cc_transcripts/ai.py` interfaces with the `llm` library to query Gemini for title generation.

## Building and Running

The project is managed with `uv` and uses `hatchling` as the build backend.

### Prerequisites
-   Python 3.11 or higher
-   `uv` (Universal Python Package Manager)

### Installation
To install the tool globally (or in a temporary environment) from the source:

```bash
uv tool install .
```

### Usage
Run the tool interactively:

```bash
cc-transcripts
```

**Options:**
*   `--output-dir`, `-o`: Specify where to save files (default: `transcripts/`).
*   `--source`, `-s`: Filter sources (`gemini`, `claude`, or `all`).

Example:
```bash
cc-transcripts --output-dir my-logs --source gemini
```

## Development Conventions

*   **Dependency Management**: Dependencies are defined in `pyproject.toml`.
*   **Code Style**: Standard Python conventions. The code uses type hinting (`typing` module) extensively.
*   **File Handling**: Paths are handled using `pathlib.Path`.
*   **Output Format**: The primary output is HTML. The `html_formatter.py` file contains the logic for rendering, including CSS and JS which are imported from `html_resources.py` (implied).
