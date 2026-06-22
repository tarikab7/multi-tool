import os
import asyncio
import markdown

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parsed Markdown</title>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            background-color: 
            color: 
            font-family: 'Outfit', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        h1, h2, h3, h4 {{
            color: 
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            background: linear-gradient(135deg, 
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            width: fit-content;
        }}
        h1 {{ border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px; font-size: 2.2em; }}
        a {{
            color: 
            text-decoration: none;
            transition: color 0.3s;
        }}
        a:hover {{
            color: 
            text-decoration: underline;
        }}
        code {{
            background-color: rgba(255,255,255,0.05);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: rgba(5,5,8,0.8);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
        }}
        pre code {{
            background: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid 
            margin: 20px 0;
            padding-left: 20px;
            color: 
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: rgba(168,85,247,0.1);
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

def convert_md_sync(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    
    html_content = markdown.markdown(text, extensions=['extra', 'codehilite'])
    
    
    full_html = HTML_TEMPLATE.format(content=html_content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    return True

async def run(params: dict):
    input_path = params.get("input_path", "").strip()
    output_path = params.get("output_path", "").strip()

    if not input_path or not output_path:
        yield {"type": "error", "message": "Both input and output paths are required."}
        return

    input_path = os.path.expanduser(input_path)
    output_path = os.path.expanduser(output_path)

    if not os.path.isfile(input_path):
        yield {"type": "error", "message": f"Markdown file '{input_path}' not found."}
        return

    
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    yield {"type": "log", "message": f"Compiling markdown: {os.path.basename(input_path)}..."}

    try:
        success = await asyncio.to_thread(convert_md_sync, input_path, output_path)
        if success:
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": f"Styled HTML document saved: {output_path}"}
            yield {"type": "success", "message": "Markdown converted successfully."}
        else:
            yield {"type": "error", "message": "Failed to compile markdown."}
            
    except Exception as e:
        yield {"type": "error", "message": f"Compilation failed: {str(e)}"}
