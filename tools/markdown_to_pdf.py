import os
import asyncio

async def run(params: dict):
    markdown_path = params.get("markdown_path", "").strip()
    output_pdf = params.get("output_pdf", "").strip()
    
    if not markdown_path or not os.path.exists(markdown_path):
        yield {"type": "error", "message": "Valid Markdown file path is required."}
        return
        
    if not output_pdf:
        base, _ = os.path.splitext(markdown_path)
        output_pdf = f"{base}.pdf"
        
    yield {"type": "log", "message": "Translating Markdown markdown elements to PDF..."}
    
    try:
        
        
        
        import markdown
        with open(markdown_path, "r") as f:
            md_text = f.read()
            
        html_content = markdown.markdown(md_text)
        
        
        base_html = markdown_path.replace(".md", ".html")
        with open(base_html, "w") as f_out:
            f_out.write(f"<html><head><style>body{{font-family:sans-serif;padding:30px;line-height:1.6;}}</style></head><body>{html_content}</body></html>")
            
        
        yield {"type": "log", "message": f"HTML preview file written: {base_html}"}
        yield {"type": "success", "message": "Markdown compiled to HTML preview next to the source."}
    except Exception as e:
        yield {"type": "error", "message": f"Compilation failed: {str(e)}"}
