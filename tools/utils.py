class ToolEvent:
    def __init__(self, type: str, **kwargs):
        self.type = type
        self.data = kwargs

    def to_dict(self):
        return {"type": self.type, **self.data}

def yield_log(message: str) -> ToolEvent:
    return ToolEvent("log", message=message)

def yield_progress(percent: float) -> ToolEvent:
    return ToolEvent("progress", percent=percent)

def yield_success(message: str, data: dict = None) -> ToolEvent:
    if data is None:
        data = {}
    return ToolEvent("success", message=message, data=data)

def yield_error(message: str) -> ToolEvent:
    return ToolEvent("error", message=message)
