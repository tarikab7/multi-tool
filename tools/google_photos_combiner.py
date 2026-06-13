import os
import json
import shutil
import tempfile
import asyncio
import subprocess
from datetime import datetime
from PIL import Image
try:
    import piexif
except ImportError:
    pass

def convert_to_exif_time(time_string):
    if not time_string:
        return None
    if isinstance(time_string, dict):
        # Handle dict format, sometimes Google Photos JSON has creationTime: {timestamp: ..., formatted: ...}
        time_string = time_string.get('formatted') or time_string.get('timestamp')
        if not time_string:
            return None
    try:
        # Check if it's a numeric timestamp
        if isinstance(time_string, (int, float)) or (isinstance(time_string, str) and time_string.isdigit()):
            dt = datetime.fromtimestamp(int(time_string))
            return dt.strftime("%Y:%m:%d %H:%M:%S")
        # Try isoformat parsing
        dt = datetime.fromisoformat(str(time_string).replace('Z', '+00:00'))
        return dt.strftime("%Y:%m:%d %H:%M:%S")
    except Exception:
        return None

def create_backup(file_path):
    backup_path = f"{file_path}.bak"
    if not os.path.exists(backup_path):
        shutil.copy(file_path, backup_path)
    return backup_path

def add_metadata_to_image(image_path, creation_time, photo_taken_time, description, geo_data):
    backup_path = create_backup(image_path)
    try:
        with Image.open(image_path) as img:
            exif_data = img.getexif()
            
            exif_time = convert_to_exif_time(photo_taken_time or creation_time)
            if exif_time:
                exif_data[36867] = exif_time  # DateTimeOriginal
                exif_data[36868] = exif_time  # DateTimeDigitized
            
            if description:
                exif_data[270] = description  # ImageDescription

            # Try to write GPS if geo_data is provided
            if geo_data and isinstance(geo_data, dict):
                # Google Photos JSON geoData can contain latitude, longitude, altitude
                lat = geo_data.get('latitude', 0.0)
                lon = geo_data.get('longitude', 0.0)
                alt = geo_data.get('altitude', 0.0)
                
                # Check if non-zero
                if lat != 0.0 or lon != 0.0:
                    try:
                        # Convert to EXIF GPS dictionary using piexif
                        gps_ifd = {}
                        
                        # Lat/Lon to EXIF rational values
                        def to_deg(value):
                            abs_val = abs(value)
                            deg = int(abs_val)
                            t1 = (abs_val - deg) * 60
                            min_val = int(t1)
                            sec_val = round((t1 - min_val) * 60, 4)
                            return ((deg, 1), (min_val, 1), (int(sec_val * 100), 100))

                        gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = b'N' if lat >= 0 else b'S'
                        gps_ifd[piexif.GPSIFD.GPSLatitude] = to_deg(lat)
                        gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = b'E' if lon >= 0 else b'W'
                        gps_ifd[piexif.GPSIFD.GPSLongitude] = to_deg(lon)
                        
                        if alt != 0.0:
                            gps_ifd[piexif.GPSIFD.GPSAltitudeRef] = 0 if alt >= 0 else 1
                            gps_ifd[piexif.GPSIFD.GPSAltitude] = (int(abs(alt) * 100), 100)

                        # Load EXIF bytes, insert GPS and save
                        exif_bytes = img.info.get('exif', b'')
                        exif_dict = piexif.load(exif_bytes) if exif_bytes else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
                        exif_dict["GPS"] = gps_ifd
                        new_exif_bytes = piexif.dump(exif_dict)
                        img.save(image_path, exif=new_exif_bytes)
                        return True
                    except Exception:
                        pass # fallback to saving without GPS EXIF dump

            img.save(image_path, exif=exif_data)
            return True
    except Exception:
        # Restore backup if error occurs
        if os.path.exists(backup_path):
            shutil.copy(backup_path, image_path)
        raise

async def add_metadata_to_video(video_path, creation_time, photo_taken_time, title, description, device_type):
    backup_path = create_backup(video_path)
    temp_path = None
    try:
        # Convert creation time to ISO 8601 string if possible
        c_time = ""
        if creation_time:
            if isinstance(creation_time, dict):
                creation_time = creation_time.get('formatted') or creation_time.get('timestamp')
            try:
                if isinstance(creation_time, (int, float)) or (isinstance(creation_time, str) and creation_time.isdigit()):
                    dt = datetime.fromtimestamp(int(creation_time))
                else:
                    dt = datetime.fromisoformat(str(creation_time).replace('Z', '+00:00'))
                c_time = dt.strftime("%Y-%m-%dT%H:%M:%S")
            except Exception:
                c_time = str(creation_time)

        metadata = {
            'title': title or "",
            'description': description or "",
            'creation_time': c_time,
            'device_type': device_type or ""
        }

        metadata_cmd = []
        for key, value in metadata.items():
            if value:
                metadata_cmd.extend(['-metadata', f'{key}={value}'])

        temp_fd, temp_path = tempfile.mkstemp(suffix='.mp4')
        os.close(temp_fd)

        cmd = ['ffmpeg', '-y', '-i', video_path, '-codec', 'copy'] + metadata_cmd + ['-map', '0', temp_path]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        await process.communicate()

        if process.returncode == 0:
            shutil.move(temp_path, video_path)
            return True
        else:
            if os.path.exists(backup_path):
                shutil.copy(backup_path, video_path)
            return False
    except Exception:
        if os.path.exists(backup_path):
            shutil.copy(backup_path, video_path)
        raise
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

async def run(params: dict):
    json_folder = params.get("json_folder", "").strip()
    media_folder = params.get("media_folder", "").strip()

    if not json_folder or not media_folder:
        yield {"type": "error", "message": "Both JSON folder and media folder are required."}
        return

    json_folder = os.path.expanduser(json_folder)
    media_folder = os.path.expanduser(media_folder)

    if not os.path.isdir(json_folder):
        yield {"type": "error", "message": f"JSON folder '{json_folder}' does not exist."}
        return
    if not os.path.isdir(media_folder):
        yield {"type": "error", "message": f"Media folder '{media_folder}' does not exist."}
        return

    # Phase 1: Build dictionary mapping lowercase filename to full absolute path (O(N) search optimization)
    yield {"type": "log", "message": "Scanning media files (building fast index)..."}
    media_index = {}
    for root, _, files in os.walk(media_folder):
        for file in files:
            # Map name to its full path
            media_index[file.lower()] = os.path.join(root, file)

    yield {"type": "log", "message": f"Indexed {len(media_index)} media file(s). Now scanning JSON files..."}

    # Gather all JSON files
    json_files = []
    for root, _, files in os.walk(json_folder):
        for file in files:
            if file.lower().endswith('.json') and file.lower() != 'metadata.json':
                json_files.append(os.path.join(root, file))

    total_json = len(json_files)
    yield {"type": "log", "message": f"Found {total_json} metadata JSON file(s). Processing..."}

    if total_json == 0:
        yield {"type": "success", "message": "Finished. 0 metadata JSONs processed."}
        return

    updated_count = 0
    not_found_count = 0
    error_count = 0

    for idx, json_path in enumerate(json_files, 1):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            if not isinstance(metadata, dict):
                continue

            title = metadata.get('title')
            if not title:
                continue

            # Look up in our optimized index
            media_path = media_index.get(title.lower())
            
            # If not found, try stripping original extension or appending json name (sometimes titles have edited endings)
            if not media_path:
                # E.g., photo.jpg.json -> photo.jpg
                # Google Photos sometimes changes titles or names
                base_json_name = os.path.basename(json_path)[:-5] # remove '.json'
                media_path = media_index.get(base_json_name.lower())

            if media_path:
                creation_time = metadata.get('creationTime')
                photo_taken_time = metadata.get('photoTakenTime')
                description = metadata.get('description', '')
                geo_data = metadata.get('geoData')
                device_type = metadata.get('deviceType', '')

                success = False
                ext = os.path.splitext(media_path)[1].lower()
                if ext in ('.jpg', '.jpeg', '.png'):
                    success = await asyncio.to_thread(
                        add_metadata_to_image, media_path, creation_time, photo_taken_time, description, geo_data
                    )
                elif ext in ('.mp4', '.mov', '.avi'):
                    success = await add_metadata_to_video(
                        media_path, creation_time, photo_taken_time, title, description, device_type
                    )
                else:
                    yield {"type": "log", "message": f"[{idx}/{total_json}] Unsupported format: {ext} for {title}"}
                    not_found_count += 1
                    continue

                if success:
                    updated_count += 1
                    yield {"type": "log", "message": f"[{idx}/{total_json}] Restored metadata for: {title}"}
                else:
                    error_count += 1
            else:
                not_found_count += 1
                # Silent or minor log to avoid clogging logs
                if not_found_count % 50 == 0 or idx == total_json:
                    yield {"type": "log", "message": f"[{idx}/{total_json}] Checked {idx} files... ({not_found_count} media files not matched so far)"}

        except Exception as e:
            error_count += 1
            yield {"type": "log", "message": f"[{idx}/{total_json}] Error processing {os.path.basename(json_path)}: {str(e)}"}

        # Yield progress occasionally to avoid web flooding
        if idx % 10 == 0 or idx == total_json:
            yield {"type": "progress", "percent": (idx / total_json) * 100}

    yield {
        "type": "success",
        "message": f"Completed. Restored {updated_count} files. Unmatched/Skipped: {not_found_count}. Errors: {error_count}."
    }
