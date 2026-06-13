import os
import asyncio

async def run(params: dict):
    pdf_path = params.get("pdf_path", "").strip()
    output_dir = params.get("output_dir", "").strip()
    
    if not pdf_path or not os.path.exists(pdf_path):
        yield {"type": "error", "message": "Valid PDF document path is required."}
        return
        
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(pdf_path), "pdf_pages")
        
    os.makedirs(output_dir, exist_ok=True)
    yield {"type": "log", "message": f"Reading PDF pages from {os.path.basename(pdf_path)}..."}
    
    try:
        # Since pdftoppm is standard on Arch Linux (poppler), we call it via subprocess
        yield {"type": "log", "message": "Calling pdftoppm renderer..."}
        cmd = ["pdftoppm", "-png", "-r", "150", pdf_path, os.path.join(output_dir, "page")]
        
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            pages = [f for f in os.listdir(output_dir) if f.startswith("page-")]
            yield {"type": "success", "message": f"Successfully extracted {len(pages)} pages to directory: {output_dir}"}
        else:
            yield {"type": "error", "message": f"pdftoppm failed: {stderr.decode()}"}
    except Exception as e:
        yield {"type": "error", "message": f"Error converting PDF: {str(e)}"}
