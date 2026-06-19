from typing import Any, Dict, Optional

class ToolEvent:
    def __init__(self, type: str, **kwargs):
        self.type = type
        self.data = kwargs

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type}
        result.update(self.data)
        return result

def yield_log(message: str) -> ToolEvent:
    return ToolEvent(type="log", message=message)

def yield_progress(percent: float) -> ToolEvent:
    return ToolEvent(type="progress", percent=percent)

def yield_success(message: str, data: Optional[Dict[str, Any]] = None) -> ToolEvent:
    kwargs = {"message": message}
    if data is not None:
        kwargs.update(data)
    return ToolEvent(type="success", **kwargs)

def yield_error(message: str) -> ToolEvent:
    return ToolEvent(type="error", message=message)
