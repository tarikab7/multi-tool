class ToolEvent:
    def __init__(self, type: str, **kwargs):
        self.type = type
        self.data = kwargs

    def to_dict(self):
        d = {"type": self.type}
        d.update(self.data)
        return d

def yield_log(msg: str) -> ToolEvent:
    return ToolEvent(type="log", message=msg)

def yield_progress(percent: float) -> ToolEvent:
    return ToolEvent(type="progress", percent=percent)

def yield_success(msg: str, data: dict = None) -> ToolEvent:
    kwargs = {"message": msg}
    if data:
        kwargs.update(data)
    return ToolEvent(type="success", **kwargs)

def yield_error(msg: str) -> ToolEvent:
    return ToolEvent(type="error", message=msg)
