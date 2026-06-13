import pytest

@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.content = b'mocked content'
            self.text = 'mocked text'

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTPError: {self.status_code}")

    def mock_get(*args, **kwargs):
        return MockResponse({"status": "mocked", "message": "This is a mocked GET response"}, 200)

    def mock_post(*args, **kwargs):
        return MockResponse({"status": "mocked", "message": "This is a mocked POST response"}, 200)

    # Patch requests module
    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("requests.post", mock_post)

@pytest.fixture(autouse=True)
def mock_httpx(monkeypatch):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.content = b'mocked content'
            self.text = 'mocked text'

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTPError: {self.status_code}")

    def mock_get(*args, **kwargs):
        return MockResponse({"status": "mocked", "message": "This is a mocked GET response"}, 200)

    def mock_post(*args, **kwargs):
        return MockResponse({"status": "mocked", "message": "This is a mocked POST response"}, 200)

    # Patch httpx module
    try:
        import httpx
        monkeypatch.setattr("httpx.get", mock_get)
        monkeypatch.setattr("httpx.post", mock_post)
    except ImportError:
        pass
