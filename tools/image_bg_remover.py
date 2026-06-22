import os
import asyncio
from PIL import Image, ImageFilter

async def run(params: dict):
    image_path = params.get("image_path", "").strip()
    tolerance = int(params.get("tolerance", "30"))
    output_path = params.get("output_path", "").strip()
    
    if not image_path or not os.path.exists(image_path):
        yield {"type": "error", "message": "Valid image path is required."}
        return
        
    if not output_path:
        base, _ = os.path.splitext(image_path)
        output_path = f"{base}_no_bg.png"
        
    yield {"type": "log", "message": "Analyzing color boundaries to separate foreground from background..."}
    await asyncio.sleep(1)
    
    try:
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        
        
        bg_color = data[0]
        
        new_data = []
        for item in data:
            
            if (abs(item[0] - bg_color[0]) <= tolerance and
                abs(item[1] - bg_color[1]) <= tolerance and
                abs(item[2] - bg_color[2]) <= tolerance):
                new_data.append((255, 255, 255, 0)) 
            else:
                new_data.append(item)
                
        img.putdata(new_data)
        img.save(output_path, "PNG")
        yield {"type": "success", "message": f"Background removed successfully. Saved to: {output_path}"}
    except Exception as e:
        yield {"type": "error", "message": f"Error processing background removal: {str(e)}"}
