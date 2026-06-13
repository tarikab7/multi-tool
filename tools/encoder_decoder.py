import base64
import urllib.parse
import asyncio

def run_codec(mode, scheme, text):
    if mode == "encode":
        if scheme == "base64":
            return base64.b64encode(text.encode('utf-8')).decode('utf-8')
        elif scheme == "url":
            return urllib.parse.quote(text)
        elif scheme == "hex":
            return text.encode('utf-8').hex()
    else:
        # Decode
        if scheme == "base64":
            return base64.b64decode(text.encode('utf-8')).decode('utf-8')
        elif scheme == "url":
            return urllib.parse.unquote(text)
        elif scheme == "hex":
            return bytes.fromhex(text).decode('utf-8')
    return ""

async def run(params: dict):
    mode = params.get("mode", "encode") # "encode" or "decode"
    scheme = params.get("scheme", "base64") # "base64", "url", "hex"
    text = params.get("text", "").strip()

    if not text:
        yield {"type": "error", "message": "Input text is required."}
        return

    yield {"type": "log", "message": f"Performing {mode} using {scheme} scheme..."}

    try:
        result = await asyncio.to_thread(run_codec, mode, scheme, text)
        yield {"type": "progress", "percent": 100.0}
        yield {"type": "log", "message": "\nResult:\n" + "="*40 + "\n" + result + "\n" + "="*40}
        yield {"type": "success", "message": "Codec operation completed successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Codec error: {str(e)}"}
