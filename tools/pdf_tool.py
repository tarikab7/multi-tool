import os
import asyncio
from PIL import Image

def compile_images_to_pdf(images_folder, output_pdf):
    # Get all image paths sorted
    extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    files = [f for f in os.listdir(images_folder) if f.lower().endswith(extensions)]
    files.sort()
    
    if not files:
        return False, "No images found in folder."

    image_list = []
    for f in files:
        filepath = os.path.join(images_folder, f)
        try:
            img = Image.open(filepath)
            # PDF requires RGB mode
            if img.mode != 'RGB':
                img = img.convert('RGB')
            image_list.append(img)
        except Exception as e:
            return False, f"Error opening {f}: {str(e)}"

    if not image_list:
        return False, "No valid images could be opened."

    try:
        # Save first image, append the rest
        image_list[0].save(output_pdf, save_all=True, append_images=image_list[1:])
        return True, f"Successfully merged {len(image_list)} images into {output_pdf}"
    except Exception as e:
        return False, f"Failed to save PDF: {str(e)}"

def extract_pdf_to_images(pdf_file, output_folder):
    try:
        # Open PDF file with PIL (Pillow can extract frames from PDF if it's openable)
        # We try to extract pages as frames
        with Image.open(pdf_file) as img:
            os.makedirs(output_folder, exist_ok=True)
            page = 0
            while True:
                out_path = os.path.join(output_folder, f"page_{page+1:03d}.jpg")
                # Convert page to RGB
                page_img = img.convert('RGB')
                page_img.save(out_path, 'JPEG')
                page += 1
                try:
                    img.seek(page)
                except EOFError:
                    break
            return True, f"Successfully extracted {page} page(s) into {output_folder}"
    except Exception as e:
        return False, f"Failed extracting PDF pages: {str(e)}. (Note: rendering PDFs requires Ghostscript on the host)."

async def run(params: dict):
    mode = params.get("mode", "images_to_pdf") # "images_to_pdf" or "pdf_to_images"
    input_path = params.get("input_path", "").strip()
    output_path = params.get("output_path", "").strip()

    if not input_path or not output_path:
        yield {"type": "error", "message": "Both input and output paths are required."}
        return

    input_path = os.path.expanduser(input_path)
    output_path = os.path.expanduser(output_path)

    if mode == "images_to_pdf":
        if not os.path.isdir(input_path):
            yield {"type": "error", "message": f"Input folder '{input_path}' does not exist."}
            return
        if not output_path.lower().endswith(".pdf"):
            yield {"type": "error", "message": "Output path must end with '.pdf'."}
            return

        yield {"type": "log", "message": f"Gathering images from {input_path}..."}
        success, msg = await asyncio.to_thread(compile_images_to_pdf, input_path, output_path)
        if success:
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": msg}
            yield {"type": "success", "message": "PDF created successfully."}
        else:
            yield {"type": "error", "message": msg}

    else:
        # PDF to images
        if not os.path.isfile(input_path):
            yield {"type": "error", "message": f"Input PDF file '{input_path}' not found."}
            return

        yield {"type": "log", "message": f"Extracting pages from '{os.path.basename(input_path)}'..."}
        success, msg = await asyncio.to_thread(extract_pdf_to_images, input_path, output_path)
        if success:
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": msg}
            yield {"type": "success", "message": "PDF pages extracted successfully."}
        else:
            yield {"type": "error", "message": msg}
