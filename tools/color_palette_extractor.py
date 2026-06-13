import os
import asyncio
from PIL import Image

async def run(params: dict):
    image_path = params.get("image_path", "").strip()
    num_colors = int(params.get("num_colors", "5"))
    
    if not image_path or not os.path.exists(image_path):
        yield {"type": "error", "message": "Valid image path is required."}
        return
        
    yield {"type": "log", "message": "Quantizing image colors and clustering dominant values..."}
    await asyncio.sleep(1)
    
    try:
        img = Image.open(image_path).convert("RGB")
        # Resize to speed up quantization
        img = img.resize((150, 150))
        
        # Quantize colors
        palette_img = img.quantize(colors=num_colors)
        palette = palette_img.getpalette()[:num_colors*3]
        
        colors = []
        for i in range(num_colors):
            r = palette[i*3]
            g = palette[i*3+1]
            b = palette[i*3+2]
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            colors.append(hex_code)
            yield {"type": "found", "message": f"Dominant Color {i+1}: {hex_code} (RGB: {r},{g},{b})"}
            
        yield {"type": "success", "message": f"Extracted palette: {', '.join(colors)}"}
    except Exception as e:
        yield {"type": "error", "message": f"Error extracting palette: {str(e)}"}
