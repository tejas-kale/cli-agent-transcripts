# CC Transcripts

A tool to export conversation history from **Gemini CLI** and **Claude Code** into clean, readable Markdown files.

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

The selected files will be saved to the `transcripts/` directory (default).

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

-   **Gemini CLI Support**: extracting chats from the temporary directory.
-   **Claude Code Support**: Parsing project-based JSONL session files.
-   **Robust Interactive Selection**: Simple text-based selection works in all terminals.
-   **Smart Titles**: Automatically extracts the first user message as the title.
-   **Clean Markdown**: Formats user prompts, model responses, and tool calls/command outputs clearly.
