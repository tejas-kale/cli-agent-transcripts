import json
import html
import markdown
from datetime import datetime
from typing import Dict, Any, List
from .html_resources import CSS, JS, BASE_TEMPLATE

def render_markdown(text: str) -> str:
    if not text:
        return ""
    # Use standard markdown with fenced code blocks
    return markdown.markdown(text, extensions=["fenced_code", "tables"])

def format_json(obj: Any) -> str:
    try:
        if isinstance(obj, str):
            obj = json.loads(obj)
        formatted = json.dumps(obj, indent=2, ensure_ascii=False)
        return f'<pre class="json">{html.escape(formatted)}</pre>'
    except (json.JSONDecodeError, TypeError):
        return f"<pre>{html.escape(str(obj))}</pre>"

def render_tool_use(tool_name: str, args: Dict[str, Any], tool_id: str) -> str:
    input_json = json.dumps(args, indent=2, ensure_ascii=False)
    
    return f"""
<div class="tool-use" data-tool-id="{tool_id}">
    <div class="tool-header"><span class="tool-icon">⚙</span> {html.escape(tool_name)}</div>
    <div class="truncatable">
        <div class="truncatable-content">
            <pre class="json">{html.escape(input_json)}</pre>
        </div>
        <button class="expand-btn">Show more</button>
    </div>
</div>
"""

def render_tool_result(result: Any, is_error: bool = False) -> str:
    content_html = format_json(result)
    error_class = ' tool-error' if is_error else ''
    
    return f"""
<div class="tool-result{error_class}">
    <div class="truncatable">
        <div class="truncatable-content">{content_html}</div>
        <button class="expand-btn">Show more</button>
    </div>
</div>
"""

def render_message(role: str, timestamp: str, content_html: str) -> str:
    if not content_html.strip():
        return ""
        
    role_class = role.lower()
    role_label = role.title()
    
    # Custom styling for tool output if needed, but generic "assistant" usually covers it
    # unless specifically separated. Claude transcripts separate "tool-reply".
    # We'll stick to user/assistant/model for now.
    
    return f"""
<div class="message {role_class}">
    <div class="message-header">
        <span class="role-label">{role_label}</span>
        <time datetime="{timestamp}" data-timestamp="{timestamp}">{timestamp}</time>
    </div>
    <div class="message-content">{content_html}</div>
</div>
"""

def format_gemini_html(session_data: Dict[str, Any], title: str = None) -> str:
    session_id = session_data.get('sessionId', 'Unknown')
    start_time = session_data.get('startTime', '')
    display_title = title if title else f"Gemini Session {session_id}"
    
    messages_html = []
    
    for msg in session_data.get('messages', []):
        role = msg.get('type', 'unknown')
        timestamp = msg.get('timestamp', '')
        content = msg.get('content', '')
        
        # Render main text content
        rendered_content = render_markdown(content)
        
        # Render tool calls
        tool_calls = msg.get('toolCalls', [])
        if tool_calls:
            for tool in tool_calls:
                tool_name = tool.get('name', 'Unknown')
                tool_id = tool.get('id', '')
                tool_args = tool.get('args', {})
                tool_result = tool.get('result', {})
                
                rendered_content += render_tool_use(tool_name, tool_args, tool_id)
                rendered_content += render_tool_result(tool_result)
        
        messages_html.append(render_message(role, timestamp, rendered_content))
        
    return BASE_TEMPLATE.format(
        title=html.escape(display_title),
        css=CSS,
        js=JS,
        session_id=session_id,
        date=start_time,
        content="".join(messages_html)
    )

def format_claude_html(session_id: str, messages: List[Dict[str, Any]], title: str = None) -> str:
    start_time = "Unknown"
    if messages:
        start_time = messages[0].get('timestamp', '')
    
    display_title = title if title else f"Claude Session {session_id}"
    
    messages_html = []
    
    for msg in messages:
        role = msg.get('type', 'unknown')
        timestamp = msg.get('timestamp', '')
        message_data = msg.get('message', {})
        content = message_data.get('content', '')
        
        rendered_content = ""
        
        if isinstance(content, str):
            rendered_content = render_markdown(content)
        elif isinstance(content, list):
            for block in content:
                if block.get('type') == 'text':
                    rendered_content += render_markdown(block.get('text', ''))
                elif block.get('type') == 'tool_use':
                    rendered_content += render_tool_use(
                        block.get('name', ''),
                        block.get('input', {}),
                        block.get('id', '')
                    )
                elif block.get('type') == 'tool_result':
                    rendered_content += render_tool_result(
                        block.get('content', ''),
                        block.get('is_error', False)
                    )
        
        messages_html.append(render_message(role, timestamp, rendered_content))

    return BASE_TEMPLATE.format(
        title=html.escape(display_title),
        css=CSS,
        js=JS,
        session_id=session_id,
        date=start_time,
        content="".join(messages_html)
    )
