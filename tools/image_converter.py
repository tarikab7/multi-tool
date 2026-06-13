import os
import asyncio
from PIL import Image

def process_single_image(input_path, output_path, target_format, width):
    try:
        with Image.open(input_path) as img:
            # Resize if width specified
            if width:
                w_percent = (width / float(img.size[0]))
                h_size = int((float(img.size[1]) * float(w_percent)))
                img = img.resize((width, h_size), Image.Resampling.LANCZOS)
            
            # Save format
            img.save(output_path, target_format)
            return True
    except Exception:
        return False

async def run(params: dict):
    input_folder = params.get("input_folder", "").strip()
    width_str = params.get("width", "").strip()
    target_format = params.get("target_format", "WEBP").upper()
    output_folder = params.get("output_folder", "").strip()

    if not input_folder or not output_folder:
        yield {"type": "error", "message": "Both input and output folders are required."}
        return

    input_folder = os.path.expanduser(input_folder)
    output_folder = os.path.expanduser(output_folder)

    if not os.path.isdir(input_folder):
        yield {"type": "error", "message": f"Input folder '{input_folder}' does not exist."}
        return

    os.makedirs(output_folder, exist_ok=True)

    width = None
    if width_str:
        try:
            width = int(width_str)
        except ValueError:
            yield {"type": "error", "message": "Width must be an integer."}
            return

    # Scan for common image formats
    image_exts = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff')
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(image_exts)]
    total_files = len(files)

    if total_files == 0:
        yield {"type": "log", "message": "No matching images found in the input folder."}
        yield {"type": "success", "message": "Finished. 0 files processed."}
        return

    yield {"type": "log", "message": f"Found {total_files} images to process. Starting..."}

    processed_count = 0
    for idx, filename in enumerate(files, 1):
        input_path = os.path.join(input_folder, filename)
        
        # Determine output filename
        name, _ = os.path.splitext(filename)
        ext = target_format.lower()
        if ext == "jpeg":
            ext = "jpg"
        output_filename = f"{name}.{ext}"
        output_path = os.path.join(output_folder, output_filename)

        try:
            success = await asyncio.to_thread(
                process_single_image, input_path, output_path, target_format, width
            )
            if success:
                processed_count += 1
                yield {"type": "log", "message": f"[{idx}/{total_files}] Converted: {filename} ➔ {output_filename}"}
            else:
                yield {"type": "log", "message": f"[{idx}/{total_files}] Failed to process: {filename}"}
        except Exception as e:
            yield {"type": "log", "message": f"[{idx}/{total_files}] Error processing {filename}: {str(e)}"}

        progress_percent = (idx / total_files) * 100
        yield {"type": "progress", "percent": progress_percent}

    yield {"type": "success", "message": f"Completed. Processed {processed_count} of {total_files} images."}
