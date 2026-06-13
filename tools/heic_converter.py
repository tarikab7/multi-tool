import os

# Ensure pillow_heif and Pillow are registered
try:
    import pillow_heif
    from PIL import Image, ImageFile
    # Disable decompression bomb protection and allow truncated images.
    Image.MAX_IMAGE_PIXELS = None
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    pillow_heif.register_heif_opener()
except ImportError:
    pass

async def run(params: dict):
    input_folder = params.get("input_folder", "").strip()
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

    heic_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.heic', '.heif'))]
    total_files = len(heic_files)

    if total_files == 0:
        yield {"type": "log", "message": "No HEIC files found in the input folder."}
        yield {"type": "success", "message": "Finished. 0 files converted."}
        return

    yield {"type": "log", "message": f"Found {total_files} HEIC file(s). Starting conversion..."}

    converted_count = 0
    for idx, filename in enumerate(heic_files, 1):
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + ".jpg"
        output_path = os.path.join(output_folder, output_filename)

        try:
            # Open the image using Pillow (pillow_heif handles HEIC files automatically)
            with Image.open(input_path) as img:
                # Try to get existing EXIF metadata, if available.
                exif = img.info.get("exif")
                if exif:
                    img.save(output_path, "JPEG", exif=exif)
                else:
                    img.save(output_path, "JPEG")
            
            converted_count += 1
            yield {"type": "log", "message": f"[{idx}/{total_files}] Converted: {filename} -> {output_filename}"}
        except Exception as e:
            yield {"type": "log", "message": f"[{idx}/{total_files}] Failed to convert {filename}: {str(e)}"}

        progress_percent = (idx / total_files) * 100
        yield {"type": "progress", "percent": progress_percent}

    yield {"type": "success", "message": f"Completed. Successfully converted {converted_count} of {total_files} HEIC files to JPEG."}
