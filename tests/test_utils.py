from tools.utils import yield_log, yield_progress, yield_success, yield_error

def test_yield_log():
    event = yield_log("hello")
    assert event.to_dict() == {"type": "log", "message": "hello"}

def test_yield_progress():
    event = yield_progress(50.0)
    assert event.to_dict() == {"type": "progress", "percent": 50.0}

def test_yield_success():
    event = yield_success("done")
    assert event.to_dict() == {"type": "success", "message": "done", "data": {}}

    event2 = yield_success("done", {"count": 5})
    assert event2.to_dict() == {"type": "success", "message": "done", "data": {"count": 5}}

def test_yield_error():
    event = yield_error("failed")
    assert event.to_dict() == {"type": "error", "message": "failed"}
