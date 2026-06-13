import asyncio
import requests

async def run(params: dict):
    text = params.get("text", "").strip()
    lang = params.get("lang", "en").strip()
    output_path = params.get("output_path", "tts_output.mp3").strip()
    
    if not text:
        yield {"type": "error", "message": "Text input is required."}
        return
        
    yield {"type": "log", "message": f"Requesting keyless Google TTS stream for: '{text[:30]}...'"}
    
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl={lang}&q={requests.utils.quote(text)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = await asyncio.to_thread(requests.get, url, headers=headers, stream=True, timeout=10)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            yield {"type": "success", "message": f"Speech file saved successfully to: {output_path}"}
        else:
            yield {"type": "error", "message": f"TTS service returned status code: {response.status_code}"}
    except Exception as e:
        yield {"type": "error", "message": f"Connection failed: {str(e)}"}
