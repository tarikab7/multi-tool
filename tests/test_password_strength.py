import pytest
from tools.password_strength import run

@pytest.mark.asyncio
async def test_password_strength_missing_params():
    # Pass an empty dictionary
    generator = run({})

    # Get the first yielded item
    first_yield = await generator.__anext__()

    # Assert it's an error and the message is correct
    assert first_yield == {"type": "error", "message": "Password string is required."}

    # Assert generator ends after yielding the error
    with pytest.raises(StopAsyncIteration):
        await generator.__anext__()

@pytest.mark.asyncio
async def test_password_strength_empty_string():
    # Pass an empty string
    generator = run({"password": "   "})

    first_yield = await generator.__anext__()
    assert first_yield == {"type": "error", "message": "Password string is required."}

    with pytest.raises(StopAsyncIteration):
        await generator.__anext__()

@pytest.mark.asyncio
async def test_password_strength_valid_weak():
    # Pass a valid weak password
    generator = run({"password": "abc"})

    events = []
    async for event in generator:
        events.append(event)

    assert len(events) > 0
    assert events[0] == {"type": "log", "message": "Calculating entropy sets..."}
    assert {"type": "found", "message": "Length: 3"} in events
    assert {"type": "found", "message": "Strength: Weak"} in events
    assert events[-1] == {"type": "success", "message": "Password analysis finished."}

@pytest.mark.asyncio
async def test_password_strength_valid_strong():
    # Pass a valid strong password
    generator = run({"password": "AveryStrongPassword123!"})

    events = []
    async for event in generator:
        events.append(event)

    assert len(events) > 0
    assert events[0] == {"type": "log", "message": "Calculating entropy sets..."}
    assert {"type": "found", "message": "Strength: Very Strong"} in events
    assert events[-1] == {"type": "success", "message": "Password analysis finished."}
