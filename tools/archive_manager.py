import os
import shutil
import tarfile
import zipfile
import asyncio
from tools.utils import yield_log, yield_progress, yield_success, yield_error

def extract_archive_sync(archive_path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    if archive_path.lower().endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
        return True, f"Extracted ZIP file into {dest_dir}"
    elif archive_path.lower().endswith(('.tar.gz', '.tgz', '.tar.xz', '.tar.bz2')):
        with tarfile.open(archive_path, 'r:*') as tar_ref:
            tar_ref.extractall(dest_dir)
        return True, f"Extracted TAR archive into {dest_dir}"
    else:
        return False, "Unsupported archive format."

def create_archive_sync(src_dir, output_archive, format_type):
    # format_type: "zip", "tar.gz", "tar.xz"
    if format_type == "zip":
        shutil.make_archive(output_archive.replace('.zip', ''), 'zip', src_dir)
        return True, f"Created ZIP archive: {output_archive}"
    elif format_type in ("tar.gz", "tar.xz"):
        ext = "gz" if "gz" in format_type else "xz"
        mode = "w:gz" if ext == "gz" else "w:xz"
        with tarfile.open(output_archive, mode) as tar:
            tar.add(src_dir, arcname=os.path.basename(src_dir))
        return True, f"Created TAR.{ext} archive: {output_archive}"
    else:
        return False, "Unsupported compression format."

async def run(params: dict):
    mode = params.get("mode", "extract") # "extract" or "create"
    input_path = params.get("input_path", "").strip()
    format_type = params.get("format", "zip").strip()
    output_folder = params.get("output_folder", "").strip()

    if not input_path or not output_folder:
        yield yield_error("Both source path and destination path are required.")
        return

    input_path = os.path.expanduser(input_path)
    output_folder = os.path.expanduser(output_folder)

    if mode == "extract":
        if not os.path.isfile(input_path):
            yield yield_error(f"Archive file '{input_path}' not found.")
            return
            
        yield yield_log(f"Extracting archive: {os.path.basename(input_path)}...")
        success, msg = await asyncio.to_thread(extract_archive_sync, input_path, output_folder)
        if success:
            yield yield_progress(100.0)
            yield yield_log(msg)
            yield yield_success("Extraction complete.")
        else:
            yield yield_error(msg)

    else:
        # Create archive
        if not os.path.isdir(input_path):
            yield yield_error(f"Source directory '{input_path}' does not exist.")
            return
            
        # Determine output file path
        archive_ext = f".{format_type}"
        if not output_folder.lower().endswith(archive_ext):
            base_folder = os.path.dirname(output_folder) if os.path.dirname(output_folder) else output_folder
            base_name = os.path.basename(input_path)
            output_file = os.path.join(base_folder, f"{base_name}{archive_ext}")
        else:
            output_file = output_folder

        yield yield_log(f"Compressing folder '{os.path.basename(input_path)}' as {format_type}...")
        success, msg = await asyncio.to_thread(create_archive_sync, input_path, output_file, format_type)
        if success:
            yield yield_progress(100.0)
            yield yield_log(msg)
            yield yield_success("Compression complete.")
        else:
            yield yield_error(msg)
