from typing import Dict, Any, Optional

class ToolEvent:
    def __init__(self, type: str, **kwargs):
        self.type = type
        self.kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type}
        result.update(self.kwargs)
        return result

def yield_log(msg: str) -> ToolEvent:
    return ToolEvent("log", message=msg)

def yield_progress(percent: float) -> ToolEvent:
    return ToolEvent("progress", percent=percent)

def yield_success(msg: str, data: Optional[Dict[str, Any]] = None) -> ToolEvent:
    kwargs = {"message": msg}
    if data is not None:
        kwargs["data"] = data
    return ToolEvent("success", **kwargs)

def yield_error(msg: str) -> ToolEvent:
    return ToolEvent("error", message=msg)
