import os
import asyncio
from PIL import Image
from PIL.ExifTags import TAGS

async def run(params: dict):
    image_path = params.get("image_path", "").strip()
    if not image_path or not os.path.exists(image_path):
        yield {"type": "error", "message": "Valid image path is required."}
        return
        
    yield {"type": "log", "message": f"Scanning EXIF headers in {os.path.basename(image_path)}..."}
    await asyncio.sleep(1)
    
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        
        if not exif_data:
            yield {"type": "log", "message": "No EXIF metadata tags found in image."}
            yield {"type": "success", "message": "Finished scan. No metadata found."}
            return
            
        found_count = 0
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            # Format large binary data
            if isinstance(value, bytes):
                value = f"<{len(value)} bytes binary data>"
            yield {"type": "found", "message": f"{tag_name}: {value}"}
            found_count += 1
            
        yield {"type": "success", "message": f"Successfully extracted {found_count} EXIF metadata tags."}
    except Exception as e:
        yield {"type": "error", "message": f"Failed reading EXIF: {str(e)}"}
