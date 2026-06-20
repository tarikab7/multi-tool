from typing import Dict, Any, Optional

class ToolEvent:
    def __init__(self, event_type: str, message: str = "", percent: Optional[float] = None, data: Optional[Dict[str, Any]] = None, **kwargs):
        self.type = event_type
        self.message = message
        self.percent = percent
        self.data = data
        self.kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type}
        if self.message:
            result["message"] = self.message
        if self.percent is not None:
            result["percent"] = self.percent
        if self.data is not None:
            result["data"] = self.data
        for k, v in self.kwargs.items():
            result[k] = v
        return result

def yield_log(msg: str) -> ToolEvent:
    return ToolEvent(event_type="log", message=msg)

def yield_progress(percent: float) -> ToolEvent:
    return ToolEvent(event_type="progress", percent=percent)

def yield_success(msg: str, data: Optional[Dict[str, Any]] = None) -> ToolEvent:
    return ToolEvent(event_type="success", message=msg, data=data)

def yield_error(msg: str) -> ToolEvent:
    return ToolEvent(event_type="error", message=msg)
