import os
import requests
import asyncio

def generate_qr_sync(text, size, output_path):
    url = "https://api.qrserver.com/v1/create-qr-code/"
    params = {
        "size": f"{size}x{size}",
        "data": text
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    return True

async def run(params: dict):
    text = params.get("text", "").strip()
    size_str = params.get("size", "300").strip()
    output_path = params.get("output_path", "").strip()

    if not text or not output_path:
        yield {"type": "error", "message": "Both text/link content and output image path are required."}
        return

    output_path = os.path.expanduser(output_path)
    if not output_path.lower().endswith(".png"):
        yield {"type": "error", "message": "Output path must end with '.png'."}
        return

    try:
        size = int(size_str)
        size = max(100, min(1000, size))
    except ValueError:
        yield {"type": "error", "message": "Size must be a valid integer between 100 and 1000."}
        return

    # Create destination directory if needed
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    yield {"type": "log", "message": f"Querying QR Server API to generate code for: '{text}'..."}

    loop = asyncio.get_running_loop()
    try:
        success = await loop.run_in_executor(None, generate_qr_sync, text, size, output_path)
        if success:
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": f"QR Code successfully saved: {output_path}"}
            yield {"type": "success", "message": "QR Code generated."}
        else:
            yield {"type": "error", "message": "Failed to save QR Code image."}
    except Exception as e:
        yield {"type": "error", "message": f"QR Code generation failed: {str(e)}"}
