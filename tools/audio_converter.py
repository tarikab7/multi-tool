import os
import subprocess
import asyncio

async def run(params: dict):
    input_path = params.get("input_path", "").strip()
    output_folder = params.get("output_folder", "").strip()

    if not input_path:
        yield {"type": "error", "message": "Input path is required."}
        return

    # Normalize paths
    input_path = os.path.expanduser(input_path)
    if output_folder:
        output_folder = os.path.expanduser(output_folder)
    else:
        # Default to same folder if single file, or parent if directory
        if os.path.isfile(input_path):
            output_folder = os.path.dirname(input_path)
        else:
            output_folder = input_path

    # Gather files to process
    files_to_process = []
    if os.path.isfile(input_path):
        files_to_process.append(input_path)
    elif os.path.isdir(input_path):
        # Scan for common video/audio extensions
        extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flac', '.wav', '.m4a', '.mp3')
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(extensions) and not "-stereo" in file:
                    files_to_process.append(os.path.join(root, file))
    else:
        yield {"type": "error", "message": f"Input path '{input_path}' does not exist."}
        return

    total_files = len(files_to_process)
    if total_files == 0:
        yield {"type": "log", "message": "No matching media files found to process."}
        yield {"type": "success", "message": "Finished. 0 files processed."}
        return

    yield {"type": "log", "message": f"Found {total_files} file(s) to process."}
    os.makedirs(output_folder, exist_ok=True)

    processed_count = 0
    for idx, filepath in enumerate(files_to_process, 1):
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        out_filename = f"{name}-stereo{ext}"
        out_filepath = os.path.join(output_folder, out_filename)

        yield {"type": "log", "message": f"[{idx}/{total_files}] Converting '{filename}' to stereo..."}

        # Upgraded FFmpeg command: Copies video track (if any) and mixes 5.1 audio down to stereo
        cmd = [
            'ffmpeg', '-y',
            '-i', filepath,
            '-filter_complex', '[0:a]pan=stereo|FL=0.5*FL+0.5*FC+0.5*SL|FR=0.5*FR+0.5*FC+0.5*SR[a]',
            '-map', '0:v?',
            '-map', '[a]',
            '-c:v', 'copy',
            '-c:a', 'aac',
            out_filepath
        ]

        try:
            # Run FFmpeg asynchronously using asyncio subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                processed_count += 1
                yield {"type": "log", "message": f"Successfully saved to: {out_filepath}"}
            else:
                err_msg = stderr.decode('utf-8', errors='ignore')
                yield {"type": "log", "message": f"Failed converting '{filename}': {err_msg[:300]}..."}
        except Exception as e:
            yield {"type": "log", "message": f"Error executing ffmpeg for '{filename}': {str(e)}"}

        progress_percent = (idx / total_files) * 100
        yield {"type": "progress", "percent": progress_percent}

    yield {"type": "success", "message": f"Completed. Successfully converted {processed_count} of {total_files} files."}
