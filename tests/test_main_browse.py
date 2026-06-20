import os
import tempfile
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_browse():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a few files and subdirectories, including ones with low ascii values
        os.mkdir(os.path.join(tmpdir, "subdir1"))
        os.mkdir(os.path.join(tmpdir, "subdir2"))
        with open(os.path.join(tmpdir, "file1.txt"), "w") as f:
            f.write("test")
        with open(os.path.join(tmpdir, "file2.txt"), "w") as f:
            f.write("test")
        with open(os.path.join(tmpdir, " file_with_space.txt"), "w") as f:
            f.write("test")
        with open(os.path.join(tmpdir, "!file_with_bang.txt"), "w") as f:
            f.write("test")

        # Call the endpoint
        response = client.get(f"/api/browse?path={tmpdir}")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "current_path" in data
        assert data["current_path"] == tmpdir

        items = data["items"]

        # Verify parent directory is present (since it's a tmpdir, it should have a parent)
        assert items[0]["name"] == ".. (Parent Directory)"
        assert items[0]["is_dir"] is True

        # We expect:
        # - .. (Parent Directory)
        # - file1.txt (file)
        # - file2.txt (file)
        # - subdir1 (dir)
        # - subdir2 (dir)
        # Order should be alphabetical by name (except parent is first because of how it's inserted, then remaining sorted)
        # Let's check they are all present
        names = [item["name"] for item in items]
        assert "file1.txt" in names
        assert "file2.txt" in names
        assert "subdir1" in names
        assert "subdir2" in names

        # Check specific properties
        for item in items:
            if item["name"] == "subdir1":
                assert item["is_dir"] is True
            elif item["name"] == "file1.txt":
                assert item["is_dir"] is False
