import os
import json
import uuid
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import httpx
import base64

import tools

app = FastAPI(title="Multi-tool API")


static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")



active_tasks: Dict[str, Dict[str, Any]] = {}

from pydantic import field_validator

class Settings(BaseModel):
    spotify_client_id: str = Field(default="", pattern=r"^([a-fA-F0-9]{32})?$")
    spotify_client_secret: str = Field(default="", pattern=r"^([a-fA-F0-9]{32})?$")
    youtube_api_keys: list[str] = Field(default_factory=list)
    last_fm_api_key: str = ""

    @field_validator("youtube_api_keys")
    @classmethod
    def validate_youtube_keys(cls, v: list[str]) -> list[str]:
        for key in v:
            if key and not key.startswith("AIzaSy"):
                raise ValueError("Invalid YouTube API Key format.")
        return v

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(config_data: dict):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")



@app.get("/")
def read_root():
    
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Multi-tool Dashboard static/index.html not found!</h1>", status_code=404)

@app.get("/api/settings", response_model=Settings)
def get_settings():
    return Settings(**load_config())

@app.post("/api/settings")
def update_settings(settings: Settings):
    save_config(settings.model_dump())
    return {"status": "success"}

@app.get("/api/settings/verify")
async def verify_settings():
    config = load_config()
    results = {}

    async with httpx.AsyncClient() as client:
        
        client_id = config.get("spotify_client_id", "")
        client_secret = config.get("spotify_client_secret", "")
        if client_id and client_secret:
            try:
                auth_str = f"{client_id}:{client_secret}"
                b64_auth_str = base64.b64encode(auth_str.encode()).decode()
                headers = {"Authorization": f"Basic {b64_auth_str}"}
                data = {"grant_type": "client_credentials"}
                r = await client.post("https://accounts.spotify.com/api/token", headers=headers, data=data, timeout=5.0)
                results["spotify"] = "valid" if r.status_code == 200 else "invalid"
            except Exception:
                results["spotify"] = "error"
        else:
            results["spotify"] = "missing"

        
        yt_keys = config.get("youtube_api_keys", [])
        if yt_keys:
            yt_status = []
            for k in yt_keys:
                if not k.startswith("AIzaSy"):
                    yt_status.append("invalid")
                    continue
                try:
                    r = await client.get(f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&key={k}", timeout=5.0)
                    
                    yt_status.append("valid" if r.status_code in (200, 400, 403) else "invalid")
                except Exception:
                    yt_status.append("error")
            results["youtube"] = yt_status
        else:
            results["youtube"] = ["missing"]

        
        lfm_key = config.get("last_fm_api_key", "")
        if lfm_key:
            try:
                r = await client.get(f"http://ws.audioscrobbler.com/2.0/?method=track.search&track=test&api_key={lfm_key}&format=json", timeout=5.0)
                results["lastfm"] = "valid" if r.status_code == 200 and "error" not in r.json() else "invalid"
            except Exception:
                results["lastfm"] = "error"
        else:
            results["lastfm"] = "missing"

    return results

import importlib



async def run_tool_task(task_id: str, tool_func, params: dict):
    queue = active_tasks[task_id]["queue"]
    try:
        
        async for event in tool_func(params):
            if hasattr(event, "to_dict"):
                event = event.to_dict()
            await queue.put(event)
            
            if event.get("type") in ("success", "error"):
                break
    except asyncio.CancelledError:
        await queue.put({"type": "log", "message": "Operation cancelled."})
        await queue.put({"type": "error", "message": "Task was stopped by the user."})
    except Exception as e:
        await queue.put({"type": "error", "message": f"Execution error: {str(e)}"})
    finally:
        
        await queue.put(None)
        active_tasks[task_id]["status"] = "finished"

@app.post("/api/run/{tool_name}")
async def run_tool(tool_name: str, params: dict, background_tasks: BackgroundTasks):
    try:
        
        module = importlib.import_module(f"tools.{tool_name}")
        tool_func = getattr(module, "run")
    except (ImportError, AttributeError) as e:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found: {str(e)}")

    
    config = load_config()
    for key, val in config.items():
        if key not in params or not params[key]:
            params[key] = val
            
    
    if "youtube_api_keys" in params and params["youtube_api_keys"]:
        params["youtube_api_key"] = params["youtube_api_keys"][0]

    task_id = str(uuid.uuid4())
    queue = asyncio.Queue()

    
    active_tasks[task_id] = {
        "queue": queue,
        "status": "running",
        "task": None
    }

    
    async_task = asyncio.create_task(run_tool_task(task_id, tool_func, params))
    active_tasks[task_id]["task"] = async_task

    return {"task_id": task_id}

@app.post("/api/cancel/{task_id}")
def cancel_task(task_id: str):
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    task_info = active_tasks[task_id]
    if task_info["status"] == "running" and task_info["task"]:
        
        task_info["task"].cancel()
        task_info["status"] = "cancelled"
        return {"status": "cancelled"}
    return {"status": "already_finished"}



@app.get("/api/stream/{task_id}")
def stream_logs(task_id: str):
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found.")

    queue = active_tasks[task_id]["queue"]

    async def event_generator():
        while True:
            event = await queue.get()
            if event is None:
                break
            
            
            event_type = event.get("type", "log")
            yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"
            
        
        if task_id in active_tasks and active_tasks[task_id]["status"] == "finished":
            del active_tasks[task_id]

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/browse")
def browse_path(path: str = ""):
    if not path:
        path = os.path.expanduser("~")
    else:
        path = os.path.expanduser(path)
        
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Path does not exist")
        
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail="Path is not a directory")
        
    try:
        items = []
        
        parent = os.path.abspath(os.path.join(path, os.pardir))
        if parent and parent != path:
            items.append({
                "name": ".. (Parent Directory)",
                "path": parent,
                "is_dir": True
            })
            
        
        
        entries = []
        with os.scandir(path) as it:
            for entry in it:
                if not entry.name.startswith('.'):
                    entries.append(entry)

        
        entries.sort(key=lambda e: e.name)

        for entry in entries:
            items.append({
                "name": entry.name,
                "path": entry.path,
                "is_dir": entry.is_dir(follow_symlinks=True)
            })
        return {
            "current_path": path,
            "items": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
