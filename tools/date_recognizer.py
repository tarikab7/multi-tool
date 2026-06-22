import os
import re
import asyncio
from datetime import datetime
from PIL import Image, UnidentifiedImageError
try:
    import piexif
except ImportError:
    pass


ERROR_CODES = {
    1: "Cannot identify image file.",
    2: "Invalid EXIF data.",
    3: "Error processing date-time from filename.",
    4: "No valid date format found in filename.",
    5: "Invalid directory path.",
    6: "Unsupported file type."
}

def extract_date_from_filename(filename):
    patterns = [
        r'(\d{8})_(\d{6})',  
        r'Screenshot_(\d{8})-(\d{6})',  
        r'VID_(\d{8})_(\d{6})',  
        r'VID-(\d{8})-WA\d{4}',  
        r'(\d{2})(\d{2})(\d{4})_(\d{2})(\d{2})(\d{2})\d*',  
        r'contact_photo_(\d{2})(\d{2})(\d{4})_(\d{2})(\d{2})(\d{2})\d*',  
        r'IMG-(\d{8})-WA\d{4}',  
        r'(\d{8})',              
        r'IMG_(\d{8})_(\d{6})',  
        r'(\d{4})-(\d{2})-(\d{2})',  
        r'(\d{4})_(\d{2})_(\d{2})',  
        r'(\d{2})-(\d{2})-(\d{4})',  
        r'(\d{2})_(\d{2})_(\d{4})'   
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            if not groups:
                continue

            date_str = None
            time_str = None

            try:
                if 'contact_photo' in pattern:
                    date_str = f"{groups[2]}{groups[1]}{groups[0]}"
                    time_str = groups[3][:6]
                else:
                    if len(groups[0]) == 8:  
                        date_str = groups[0]
                        time_str = groups[1] if len(groups) > 1 else '000000'
                    elif len(groups[0]) == 2:  
                        date_str = f"{groups[2]}{groups[1]}{groups[0]}"
                        time_str = ''.join(groups[3:6]) if len(groups) > 3 else '000000'
                    else:
                        date_str = ''.join(groups[:3])
                        time_str = ''.join(groups[3:6]) if len(groups) > 3 else '000000'

                time_str = time_str[:6].ljust(6, '0')
                date_time_str = date_str + time_str
                return datetime.strptime(date_time_str, '%Y%m%d%H%M%S')
            except Exception:
                pass
    return None

def get_exif_date(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                date_str = exif_data.get(36867)  
                if date_str:
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except Exception:
        pass
    return None

def update_exif_date(image_path, date_time):
    try:
        with Image.open(image_path) as img:
            exif_data = img.info.get('exif', b'')
            exif_dict = piexif.load(exif_data) if exif_data else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
            
            date_str = date_time.strftime('%Y:%m:%d %H:%M:%S')
            exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str.encode('utf-8')
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode('utf-8')
            exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode('utf-8')

            exif_bytes = piexif.dump(exif_dict)
            img.save(image_path, exif=exif_bytes)
            return True
    except Exception:
        return False

def extract_year_from_folder(folder_name):
    match = re.search(r'\b(19|20)\d{2}\b', folder_name)
    return int(match.group(0)) if match else None

def process_file_sync(file_path, folder_year):
    filename = os.path.basename(file_path)
    date_time = extract_date_from_filename(filename)

    
    if not date_time and file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        date_time = get_exif_date(file_path)

    
    if not date_time and folder_year:
        date_time = datetime(folder_year, 1, 1)

    if not date_time:
        return False, None

    if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        success = update_exif_date(file_path, date_time)
        return success, date_time
    elif file_path.lower().endswith(('.mp4', '.avi', '.mov')):
        
        
        return True, date_time
    else:
        return False, None

async def run(params: dict):
    directory = params.get("directory", "").strip()

    if not directory:
        yield {"type": "error", "message": "Directory path is required."}
        return

    directory = os.path.expanduser(directory)
    if not os.path.exists(directory):
        yield {"type": "error", "message": f"Directory '{directory}' does not exist."}
        return

    
    files_to_process = []
    for root, dirs, files in os.walk(directory):
        folder_year = extract_year_from_folder(os.path.basename(root))
        for filename in files:
            file_path = os.path.join(root, filename)
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov')):
                files_to_process.append((file_path, folder_year))

    total_files = len(files_to_process)
    yield {"type": "log", "message": f"Found {total_files} media files to examine."}

    if total_files == 0:
        yield {"type": "success", "message": "Finished. 0 files processed."}
        return

    updated_count = 0
    skipped_count = 0

    for idx, (file_path, folder_year) in enumerate(files_to_process, 1):
        filename = os.path.basename(file_path)
        
        try:
            success, date_time = await asyncio.to_thread(process_file_sync, file_path, folder_year)
            if success and date_time:
                updated_count += 1
                yield {"type": "log", "message": f"[{idx}/{total_files}] Updated {filename} -> {date_time.strftime('%Y-%m-%d %H:%M:%S')}"}
            else:
                skipped_count += 1
        except Exception as e:
            skipped_count += 1
            yield {"type": "log", "message": f"[{idx}/{total_files}] Error processing {filename}: {str(e)}"}

        if idx % 10 == 0 or idx == total_files:
            yield {"type": "progress", "percent": (idx / total_files) * 100}

    yield {"type": "success", "message": f"Completed. Updated: {updated_count} files. Skipped: {skipped_count}."}
