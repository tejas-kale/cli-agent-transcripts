# CC Transcripts

A tool to export conversation history from **Gemini CLI** and **Claude Code** into clean, readable, and interactive HTML files.

## Installation

You can install this tool using `uv`:

```bash
uv tool install .
```

## Usage

Run the tool to interactively select and save transcripts:

```bash
cc-transcripts
```

The tool will display a list of the **10 latest** sessions. You can enter:
-   **Numbers** (e.g., `1` or `1 3 5`) to save specific transcripts.
-   **`all`** to save all 10 displayed transcripts.
-   **`q`** to quit.

The selected files will be saved to the `transcripts/` directory by default.

### Options

Specify an output directory:

```bash
cc-transcripts --output-dir my-logs
```

Filter by source (Gemini or Claude) before listing:

```bash
cc-transcripts --source gemini
```

## Features

-   **Multi-Source Support**: 
    -   **Gemini CLI**: Automatically finds and extracts chats from `~/.gemini/tmp/`.
    -   **Claude Code**: Parses project-based JSONL session files from `~/.claude/projects/`.
-   **Interactive Selection**: Easily browse and select recent sessions directly from your terminal.
-   **AI-Powered Titles**: Uses Gemini (via the `llm` library) to generate concise, descriptive titles for your transcripts based on their content.
-   **Beautiful HTML Export**:
    -   Clean, modern design.
    -   Syntax highlighting for code blocks.
    -   **Collapsible Tool Calls**: Detailed view of tool inputs and results that stays out of the way until you need it.
-   **Automatic Sanitization**: Filenames are automatically sanitized for compatibility across different operating systems.
