def yield_log(msg: str) -> dict:
    return {"type": "log", "message": msg}

def yield_progress(percent: float) -> dict:
    return {"type": "progress", "progress": percent}

def yield_success(msg: str, data: dict = None) -> dict:
    result = {"type": "success", "message": msg}
    if data is not None:
        result["data"] = data
    return result

def yield_error(msg: str) -> dict:
    return {"type": "error", "message": msg}
