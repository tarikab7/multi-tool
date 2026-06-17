import pytest
import datetime
from tools.ssl_expiry_checker import run

@pytest.mark.asyncio
async def test_ssl_expiry_missing_host():
    gen = run({})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert len(dicts) == 1
    assert dicts[0]["type"] == "error"
    assert "required" in dicts[0]["message"]

@pytest.mark.asyncio
async def test_ssl_expiry_success(mocker):
    # Mocking
    mock_context = mocker.patch('ssl.create_default_context')
    mock_conn = mocker.patch('socket.create_connection')

    mock_sock = mocker.MagicMock()
    mock_context.return_value.wrap_socket.return_value = mock_sock

    future_date = datetime.datetime.utcnow() + datetime.timedelta(days=100)
    expiry_str = future_date.strftime("%b %d %H:%M:%S %Y GMT")

    mock_sock.getpeercert.return_value = {
        "notAfter": expiry_str,
        "issuer": []
    }

    gen = run({"host": "example.com"})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert dicts[0]["type"] == "log"
    assert dicts[1]["type"] == "found"
    assert dicts[2]["type"] == "found"
    assert dicts[3]["type"] == "found"
    assert dicts[4]["type"] == "success"
    assert "OK (100 days remaining)" in dicts[4]["message"] or "OK (99 days remaining)" in dicts[4]["message"]

@pytest.mark.asyncio
async def test_ssl_expiry_expired(mocker):
    # Mocking
    mock_context = mocker.patch('ssl.create_default_context')
    mock_conn = mocker.patch('socket.create_connection')

    mock_sock = mocker.MagicMock()
    mock_context.return_value.wrap_socket.return_value = mock_sock

    past_date = datetime.datetime.utcnow() - datetime.timedelta(days=10)
    expiry_str = past_date.strftime("%b %d %H:%M:%S %Y GMT")

    mock_sock.getpeercert.return_value = {
        "notAfter": expiry_str,
        "issuer": []
    }

    gen = run({"host": "example.com"})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert dicts[4]["type"] == "log"
    assert "EXPIRED" in dicts[4]["message"]
    assert dicts[5]["type"] == "success"
