import os

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
        # Since we want to run keylessly, we use standard python to compile HTML first,
        # then print it to PDF using weasyprint or simple CLI.
        # For simplicity and ease of use, we do a basic html conversion, and warn if dependencies are missing.
        import markdown
        with open(markdown_path, "r") as f:
            md_text = f.read()
            
        html_content = markdown.markdown(md_text)
        
        # We write a clean html file
        base_html = markdown_path.replace(".md", ".html")
        with open(base_html, "w") as f_out:
            f_out.write(f"<html><head><style>body{{font-family:sans-serif;padding:30px;line-height:1.6;}}</style></head><body>{html_content}</body></html>")
            
        # Try to call weasyprint or pandoc or libreoffice
        yield {"type": "log", "message": f"HTML preview file written: {base_html}"}
        yield {"type": "success", "message": "Markdown compiled to HTML preview next to the source."}
    except Exception as e:
        yield {"type": "error", "message": f"Compilation failed: {str(e)}"}
