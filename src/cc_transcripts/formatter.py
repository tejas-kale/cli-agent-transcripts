import json
from datetime import datetime
from typing import Dict, List, Any

def format_timestamp(ts_str: str) -> str:
    try:
        # Attempt to parse ISO format
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return str(ts_str)

def extract_title(transcript: Dict[str, Any]) -> str:
    """Extract a short title from the transcript's first meaningful user message."""
    messages = []
    if transcript['source'] == 'gemini':
        messages = transcript['data'].get('messages', [])
    elif transcript['source'] == 'claude':
        messages = transcript.get('messages', [])
    
    for msg in messages:
        role = msg.get('type', '')
        content = ""
        
        if transcript['source'] == 'gemini' and role == 'user':
            content = msg.get('content', '')
        elif transcript['source'] == 'claude' and role == 'user':
            content = msg.get('message', {}).get('content', '')
            if not isinstance(content, str):
                 content = str(content)

        if content and content.strip():
            # Skip system/caveat messages common in Claude logs
            if "<local-command-caveat>" in content:
                continue
                
            # Clean up newlines and truncate
            clean_content = " ".join(content.split()).strip()
            
            # Remove common command tags for cleaner titles if present
            clean_content = clean_content.replace("<command-name>", "/").replace("</command-name>", "")
            
            return (clean_content[:60] + '...') if len(clean_content) > 60 else clean_content
            
    return "No title found"

def format_gemini_markdown(session_data: Dict[str, Any], title: str = None) -> str:
    md = []
    
    # Header
    session_id = session_data.get('sessionId', 'Unknown Session')
    start_time = format_timestamp(session_data.get('startTime', ''))
    
    # Title is now used only for the filename as per user request
    md.append(f"**Date:** {start_time}")
    md.append(f"**Session ID:** {session_id}\n")
    md.append("---\n")
    
    for msg in session_data.get('messages', []):
        role = msg.get('type', 'unknown').title()
        timestamp = format_timestamp(msg.get('timestamp', ''))
        content = msg.get('content', '')
        
        md.append(f"### {role} ({timestamp})")
        
        if content:
            md.append(content)
            md.append("")
            
        tool_calls = msg.get('toolCalls', [])
        if tool_calls:
            md.append("\n<details>")
            md.append("<summary>Tool Calls</summary>\n")
            for tool in tool_calls:
                md.append(f"**Tool:** `{tool.get('name')}`")
                md.append("```json")
                md.append(json.dumps(tool.get('args', {}), indent=2))
                md.append("```")
                md.append("**Result:**")
                md.append("```json")
                md.append(json.dumps(tool.get('result', {}), indent=2))
                md.append("```")
            md.append("</details>\n")
            
    return "\n".join(md)

def format_claude_markdown(session_id: str, messages: List[Dict[str, Any]], title: str = None) -> str:
    md = []
    
    # Header
    # Try to find the first timestamp
    start_time = "Unknown"
    if messages:
        start_time = format_timestamp(messages[0].get('timestamp', ''))

    # Title is now used only for the filename as per user request
    md.append(f"**Date:** {start_time}")
    md.append(f"**Session ID:** {session_id}\n")
    md.append("---\n")
    
    for msg in messages:
        role = msg.get('type', 'unknown').title()
        timestamp = format_timestamp(msg.get('timestamp', ''))
        content = msg.get('message', {}).get('content', '')
        
        # Claude specific: content can be complex or just a string
        # In the JSONL logs seen, user content is often XML-like
        
        md.append(f"### {role} ({timestamp})")
        
        if isinstance(content, str):
            # Clean up some common XML tags for readability if desired, 
            # or just dump them in a code block if they look like code.
            # For now, let's just print it.
            md.append(content)
        else:
             md.append(str(content))
        
        md.append("")
        
    return "\n".join(md)