import os
import asyncio
import requests
import json
import re
import yt_dlp as youtube_dl

def fetch_spotify_playlist_tracks(playlist_url):
    """
    Scrapes a public Spotify playlist page keylessly.
    Fetches the embed player endpoint and extracts track titles and artists from __NEXT_DATA__.
    """
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    embed_url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    response = requests.get(embed_url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Spotify playlist embed (HTTP {response.status_code})")
        
    match = re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>', response.text, re.DOTALL)
    if not match:
        raise Exception("Could not parse Spotify playlist metadata (missing script block)")
        
    try:
        js = json.loads(match.group(1))
        state_data = js.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {})
        entity = state_data.get("entity", {})
        track_list = entity.get("trackList", [])
        
        tracks = []
        for track in track_list:
            title = track.get("title")
            artist = track.get("subtitle")
            if title:
                tracks.append(f"{title} - {artist or 'Unknown Artist'}")
        return tracks
    except Exception as e:
        raise Exception(f"Error parsing playlist JSON: {str(e)}")

def fetch_youtube_url_yt_dlp(track_name):
    """
    Searches YouTube keylessly for a track using yt-dlp.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': 'in_playlist',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(f"ytsearch:{track_name}", download=False)
        if 'entries' in info_dict and len(info_dict['entries']) > 0:
            video_id = info_dict['entries'][0]['id']
            return f'https://www.youtube.com/watch?v={video_id}'
    return None

def download_track(track_name, video_url, download_path):
    """
    Downloads audio from a YouTube video URL and saves it as MP3 with basic metadata.
    """
    parts = track_name.split(" - ")
    title = parts[0]
    artist = parts[1] if len(parts) > 1 else "Unknown"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, f'{track_name}.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'postprocessor_args': [
            '-metadata', f'title={title}',
            '-metadata', f'artist={artist}',
            '-metadata', 'album=Spotify Downloader'
        ],
        'noplaylist': True,
        'quiet': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

async def run(params: dict):
    playlist_urls = params.get("playlist_urls", [])
    download_path = params.get("download_path", "downloads").strip()
    
    if isinstance(playlist_urls, str):
        playlist_urls = [url.strip() for url in playlist_urls.split(",") if url.strip()]

    if not playlist_urls:
        yield {"type": "error", "message": "Spotify playlist URL(s) required."}
        return

    download_path = os.path.expanduser(download_path)
    os.makedirs(download_path, exist_ok=True)

    # Resolve all tracks from all playlists
    all_tracks = []
    
    for playlist_url in playlist_urls:
        yield {"type": "log", "message": f"Fetching keyless playlist metadata: {playlist_url}"}
        try:
            tracks = await asyncio.to_thread(fetch_spotify_playlist_tracks, playlist_url)
            all_tracks.extend(tracks)
        except Exception as e:
            yield {"type": "log", "message": f"Error fetching playlist details: {str(e)}"}

    total_tracks = len(all_tracks)
    yield {"type": "log", "message": f"Total tracks loaded keylessly: {total_tracks}"}

    if total_tracks == 0:
        yield {"type": "success", "message": "Finished. No tracks found."}
        return

    downloaded_count = 0
    skipped_count = 0

    # Scan existing files to avoid duplicate downloads
    existing_songs = set()
    if os.path.exists(download_path):
        for filename in os.listdir(download_path):
            if filename.endswith(".mp3"):
                existing_songs.add(os.path.splitext(filename)[0].lower())

    for idx, track_name in enumerate(all_tracks, 1):
        clean_track_name = track_name.replace("/", "_").replace("\\", "_")
        
        # Check if already downloaded
        if clean_track_name.lower() in existing_songs:
            yield {"type": "log", "message": f"[{idx}/{total_tracks}] Skipping already downloaded: {track_name}"}
            skipped_count += 1
            progress_percent = (idx / total_tracks) * 100
            yield {"type": "progress", "percent": progress_percent}
            continue

        yield {"type": "log", "message": f"[{idx}/{total_tracks}] Resolving: {track_name}"}

        # Try to search YouTube URL using yt-dlp keyless search
        video_url = None
        try:
            video_url = await asyncio.to_thread(fetch_youtube_url_yt_dlp, track_name)
        except Exception as e:
            yield {"type": "log", "message": f"Search failed: {str(e)}"}

        if not video_url:
            yield {"type": "log", "message": f"Could not find YouTube matches for: {track_name}"}
            skipped_count += 1
            progress_percent = (idx / total_tracks) * 100
            yield {"type": "progress", "percent": progress_percent}
            continue

        # Download from YouTube
        try:
            yield {"type": "log", "message": f"Downloading audio from YouTube match..."}
            await asyncio.to_thread(download_track, clean_track_name, video_url, download_path)
            downloaded_count += 1
            yield {"type": "log", "message": f"Successfully downloaded: {track_name}"}
        except Exception as e:
            yield {"type": "log", "message": f"Error downloading {track_name}: {str(e)}"}
            skipped_count += 1

        progress_percent = (idx / total_tracks) * 100
        yield {"type": "progress", "percent": progress_percent}

    yield {"type": "success", "message": f"Completed. Downloaded {downloaded_count} songs. Skipped/Failed {skipped_count}."}
