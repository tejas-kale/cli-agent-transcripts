import json
import os
import glob
from pathlib import Path
from typing import List, Dict, Any, Generator

class TranscriptParser:
    def __init__(self):
        self.home = Path.home()

    def get_gemini_transcripts(self) -> Generator[Dict[str, Any], None, None]:
        gemini_tmp = self.home / ".gemini" / "tmp"
        if not gemini_tmp.exists():
            return

        # Pattern: .gemini/tmp/<hash>/chats/session-*.json
        pattern = str(gemini_tmp / "*" / "chats" / "session-*.json")
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Enforce structure or add metadata
                    if 'sessionId' in data:
                        yield {
                            'source': 'gemini',
                            'data': data,
                            'filename': Path(file_path).name,
                            'path': file_path
                        }
            except Exception as e:
                print(f"Error parsing Gemini file {file_path}: {e}")

    def get_claude_transcripts(self) -> Generator[Dict[str, Any], None, None]:
        claude_projects = self.home / ".claude" / "projects"
        if not claude_projects.exists():
            return

        # Pattern: .claude/projects/<project_dir>/*.jsonl
        # The session files seem to be UUID.jsonl
        pattern = str(claude_projects / "*" / "*.jsonl")
        
        for file_path in glob.glob(pattern):
            # rudimentary check if it looks like a session file (uuid-like)
            if "agent-" in Path(file_path).name: # Skip agent logs if they are distinct
                 continue
            
            messages = []
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip(): continue
                        try:
                            entry = json.loads(line)
                            # Filter for relevant types
                            if entry.get('type') in ['user', 'assistant', 'model']:
                                messages.append(entry)
                        except json.JSONDecodeError:
                            continue
                
                if messages:
                    # Extract session ID from filename
                    session_id = Path(file_path).stem
                    yield {
                        'source': 'claude',
                        'id': session_id,
                        'messages': messages,
                        'filename': Path(file_path).name,
                        'path': file_path
                    }

            except Exception as e:
                print(f"Error parsing Claude file {file_path}: {e}")

    def get_all_transcripts(self, source: str = 'all') -> Generator[Dict[str, Any], None, None]:
        if source in ['all', 'gemini']:
            yield from self.get_gemini_transcripts()
        if source in ['all', 'claude']:
            yield from self.get_claude_transcripts()
