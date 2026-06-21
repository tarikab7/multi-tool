class ToolEvent:
    def __init__(self, type_val: str, **kwargs):
        self.type = type_val
        self.kwargs = kwargs

    def to_dict(self):
        d = {"type": self.type}
        d.update(self.kwargs)
        return d

def yield_log(msg: str) -> ToolEvent:
    return ToolEvent("log", message=msg)

def yield_progress(percent: float) -> ToolEvent:
    return ToolEvent("progress", percent=percent)

def yield_success(msg: str, data: dict = None) -> ToolEvent:
    kwargs = {"message": msg}
    if data is not None:
        kwargs["data"] = data
    return ToolEvent("success", **kwargs)

def yield_error(msg: str) -> ToolEvent:
    return ToolEvent("error", message=msg)
