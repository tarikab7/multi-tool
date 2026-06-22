import os
import requests
import asyncio
import xml.etree.ElementTree as ET

async def run(params: dict):
    bucket_name = params.get("bucket_name", "").strip()
    download_dir = params.get("download_dir", "s3_downloads").strip()
    
    if not bucket_name:
        yield {"type": "error", "message": "Bucket name is required."}
        return
        
    os.makedirs(download_dir, exist_ok=True)
    yield {"type": "log", "message": f"Retrieving public S3 bucket directory listings for '{bucket_name}'..."}
    
    url = f"https://{bucket_name}.s3.amazonaws.com/"
    
    try:
        response = await asyncio.to_thread(requests.get, url, timeout=10)
        if response.status_code != 200:
            yield {"type": "error", "message": f"Failed listing bucket contents (HTTP {response.status_code})"}
            return
            
        root = ET.fromstring(response.content)
        
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        
        keys = []
        for content in root.findall("s3:Contents", ns):
            key = content.find("s3:Key", ns).text
            size = int(content.find("s3:Size", ns).text)
            if size > 0:
                keys.append((key, size))
                
        yield {"type": "log", "message": f"Found {len(keys)} public files in bucket."}
        
        downloaded = 0
        for key, size in keys[:20]: 
            file_url = f"{url}{key}"
            dest_path = os.path.join(download_dir, key)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            yield {"type": "log", "message": f"Downloading: {key} ({size / 1024:.1f} KB)..."}
            r_file = await asyncio.to_thread(requests.get, file_url, timeout=10)
            if r_file.status_code == 200:
                with open(dest_path, "wb") as f:
                    f.write(r_file.content)
                downloaded += 1
            await asyncio.sleep(0.1)
            
        yield {"type": "success", "message": f"Downloaded {downloaded} files into {download_dir}."}
    except Exception as e:
        yield {"type": "error", "message": f"S3 Bucket read failed: {str(e)}"}
