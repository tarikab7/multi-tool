import os
import re
import asyncio
import requests
import musicbrainzngs
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, error


musicbrainzngs.set_useragent("MP3MetadataUpdater", "1.0", "your_email@example.com")

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def fetch_itunes_data(title, artist):
    """
    Fetches track metadata and high-res cover art keylessly using the iTunes Search API.
    """
    query = f"{artist} {title}"
    url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&entity=song&limit=1"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("resultCount", 0) > 0:
                song = data["results"][0]
                art100 = song.get("artworkUrl100")
                cover_url = None
                if art100:
                    
                    cover_url = art100.replace("100x100bb.jpg", "600x600bb.jpg")
                return {
                    "title": song.get("trackName", title),
                    "artist": song.get("artistName", artist),
                    "genre": song.get("primaryGenreName", "Unknown Genre"),
                    "album": song.get("collectionName", "Unknown Album"),
                    "cover_url": cover_url
                }
    except Exception:
        pass
    return None

def fetch_musicbrainz_data(title, artist):
    """
    Fetches track metadata keylessly using the MusicBrainz XML/JSON API.
    """
    try:
        result = musicbrainzngs.search_recordings(recording=title, artist=artist, limit=1)
        if result.get('recording-list'):
            recording = result['recording-list'][0]
            album = recording['release-list'][0]['title'] if 'release-list' in recording else 'Unknown Album'
            genre = recording['tag-list'][0]['name'] if 'tag-list' in recording else 'Unknown Genre'
            return {
                "title": recording['title'],
                "artist": recording['artist-credit'][0]['artist']['name'],
                "genre": genre,
                "album": album,
                "cover_url": None
            }
    except Exception:
        pass
    return None

def download_image(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None

def update_metadata(file_path, new_filename, music_data):
    new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
    if not os.path.exists(new_file_path):
        os.rename(file_path, new_file_path)
        file_path = new_file_path

    
    try:
        audio = ID3(file_path)
    except error:
        
        audio = ID3()
    
    audio.add(TIT2(encoding=3, text=music_data.get('title', '')))
    audio.add(TPE1(encoding=3, text=music_data.get('artist', '')))
    audio.add(TALB(encoding=3, text=music_data.get('album', '')))
    audio.add(TCON(encoding=3, text=music_data.get('genre', '')))

    cover_url = music_data.get('cover_url')
    if cover_url:
        cover_image = download_image(cover_url)
        if cover_image:
            audio.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,  
                desc='Cover',
                data=cover_image
            ))
    
    audio.save(file_path)
    return new_file_path

async def run(params: dict):
    mp3_directory = params.get("mp3_directory", "").strip()

    if not mp3_directory:
        yield {"type": "error", "message": "MP3 directory is required."}
        return

    mp3_directory = os.path.expanduser(mp3_directory)
    if not os.path.isdir(mp3_directory):
        yield {"type": "error", "message": f"Directory '{mp3_directory}' does not exist."}
        return

    mp3_files = [f for f in os.listdir(mp3_directory) if f.lower().endswith(".mp3")]
    total_files = len(mp3_files)

    if total_files == 0:
        yield {"type": "log", "message": "No MP3 files found in the specified directory."}
        yield {"type": "success", "message": "Finished. 0 files processed."}
        return

    yield {"type": "log", "message": f"Found {total_files} MP3 file(s). Updating metadata keylessly..."}

    updated_count = 0
    for idx, filename in enumerate(mp3_files, 1):
        file_path = os.path.join(mp3_directory, filename)
        yield {"type": "log", "message": f"[{idx}/{total_files}] Processing tags for: {filename}"}

        
        try:
            audio = EasyID3(file_path)
            title = audio.get('title', [os.path.splitext(filename)[0]])[0]
            artist = audio.get('artist', ['Unknown Artist'])[0]
        except Exception:
            title = os.path.splitext(filename)[0]
            artist = 'Unknown Artist'

        
        music_data = None
        
        
        music_data = await asyncio.to_thread(fetch_itunes_data, title, artist)
        
        
        if not music_data:
            music_data = await asyncio.to_thread(fetch_musicbrainz_data, title, artist)

        
        if not music_data:
            music_data = {
                "title": title,
                "artist": artist,
                "genre": "Unknown Genre",
                "album": "Unknown Album",
                "cover_url": None
            }

        sanitized_artist = sanitize_filename(music_data['artist'])
        sanitized_title = sanitize_filename(music_data['title'])
        new_filename = f"{sanitized_artist} - {sanitized_title}.mp3"

        
        try:
            await asyncio.to_thread(update_metadata, file_path, new_filename, music_data)
            updated_count += 1
            yield {"type": "log", "message": f"Saved tag: {new_filename}"}
        except Exception as e:
            yield {"type": "log", "message": f"Failed updating {filename}: {str(e)}"}

        progress_percent = (idx / total_files) * 100
        yield {"type": "progress", "percent": progress_percent}

    yield {"type": "success", "message": f"Completed. Successfully updated metadata for {updated_count} of {total_files} MP3 files."}
