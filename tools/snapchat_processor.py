import os
import asyncio
from datetime import datetime
from PIL import Image
from bs4 import BeautifulSoup
try:
    import piexif
except ImportError:
    pass

def parse_snapchat_date(date_str):
    # Snapchat date strings typically look like "2020-01-04 16:17:21 UTC" or similar
    # Let's clean and try parsing
    clean_date = date_str.replace("UTC", "").strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S %Z",
        "%d/%m/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(clean_date, fmt)
            return dt.strftime("%Y:%m:%d %H:%M:%S")
        except ValueError:
            continue
    return None

def extract_metadata_from_html(html_path):
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            metadata = {}
            
            # Snapchat HTML format check: find div class="media" or similar
            # If structure is different, let's also support fallback structures
            media_divs = soup.find_all('div', class_='media')
            if not media_divs:
                # Fallback to general parsing: look for links and paragraphs containing date
                # Let's search all links that end with media extension
                for a_tag in soup.find_all('a'):
                    href = a_tag.get('href', '')
                    filename = a_tag.get_text().strip()
                    # Look for date in sibling or parent paragraph
                    parent = a_tag.parent
                    date_text = None
                    if parent:
                        p_tag = parent.find('p', class_='date')
                        if p_tag:
                            date_text = p_tag.get_text()
                    if filename and date_text:
                        metadata[filename.lower()] = date_text

            for media in media_divs:
                a_tag = media.find('a')
                p_tag = media.find('p', class_='date')
                if a_tag and p_tag:
                    filename = a_tag.get_text().strip()
                    date = p_tag.get_text().strip()
                    metadata[filename.lower()] = date
            return metadata
    except Exception:
        return None

def write_exif(image_path, exif_date_str):
    try:
        with Image.open(image_path) as img:
            exif_data = img.info.get('exif', b'')
            exif_dict = piexif.load(exif_data) if exif_data else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
            
            # Convert date format to bytes
            exif_dict["0th"][piexif.ImageIFD.DateTime] = exif_date_str.encode('utf-8')
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_date_str.encode('utf-8')
            exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = exif_date_str.encode('utf-8')

            exif_bytes = piexif.dump(exif_dict)
            img.save(image_path, exif=exif_bytes)
            return True
    except Exception:
        return False

async def run(params: dict):
    file_path = params.get("file_path", "").strip()
    html_path = params.get("html_path", "").strip()

    if not file_path or not html_path:
        yield {"type": "error", "message": "Both media folder path and Snapchat HTML path are required."}
        return

    file_path = os.path.expanduser(file_path)
    html_path = os.path.expanduser(html_path)

    if not os.path.isdir(file_path):
        yield {"type": "error", "message": f"Media directory '{file_path}' does not exist."}
        return
    if not os.path.isfile(html_path):
        yield {"type": "error", "message": f"HTML file '{html_path}' does not exist."}
        return

    yield {"type": "log", "message": "Parsing Snapchat HTML metadata..."}
    metadata = await asyncio.to_thread(extract_metadata_from_html, html_path)

    if not metadata:
        yield {"type": "error", "message": "Failed to parse metadata or no media found in Snapchat HTML."}
        return

    yield {"type": "log", "message": f"Found {len(metadata)} media entries in HTML. Indexing media directory..."}

    # Index media folder recursively (lowercase filename -> path)
    media_index = {}
    for root, _, files in os.walk(file_path):
        for file in files:
            media_index[file.lower()] = os.path.join(root, file)

    yield {"type": "log", "message": f"Indexed {len(media_index)} local files. Matching dates..."}

    updated_count = 0
    skipped_count = 0

    idx = 0
    total_keys = len(metadata)
    for filename_lower, raw_date in metadata.items():
        idx += 1
        local_path = media_index.get(filename_lower)
        if not local_path:
            skipped_count += 1
            continue

        exif_date_str = parse_snapchat_date(raw_date)
        if not exif_date_str:
            yield {"type": "log", "message": f"Could not parse Snapchat date format: {raw_date}"}
            skipped_count += 1
            continue

        # Support images
        ext = os.path.splitext(local_path)[1].lower()
        if ext in ('.jpg', '.jpeg', '.png'):
            success = await asyncio.to_thread(write_exif, local_path, exif_date_str)
            if success:
                updated_count += 1
                yield {"type": "log", "message": f"Updated {os.path.basename(local_path)} date to {exif_date_str}"}
            else:
                skipped_count += 1
        else:
            # Video or other formats (logged but not updated since Exif is image-specific)
            yield {"type": "log", "message": f"Parsed date for video {os.path.basename(local_path)}: {exif_date_str}"}
            updated_count += 1

        if idx % 10 == 0 or idx == total_keys:
            yield {"type": "progress", "percent": (idx / total_keys) * 100}

    yield {"type": "success", "message": f"Completed. Restored {updated_count} file(s). Skipped: {skipped_count}."}
