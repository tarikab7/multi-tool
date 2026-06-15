class ToolEvent:
    def __init__(self, **kwargs):
        self.data = kwargs

    def to_dict(self):
        return self.data


def yield_log(msg: str) -> ToolEvent:
    return ToolEvent(type="log", message=msg)

def yield_progress(percent: float) -> ToolEvent:
    return ToolEvent(type="progress", percent=percent)

def yield_success(msg: str, data: dict = None) -> ToolEvent:
    event_data = {"type": "success", "message": msg}
    if data:
        event_data.update(data)
    return ToolEvent(**event_data)

def yield_error(msg: str) -> ToolEvent:
    return ToolEvent(type="error", message=msg)
