import pytest
from tools.folder_analyzer import format_size

@pytest.mark.parametrize(
    "size_bytes, expected",
    [
        (0, "0 Bytes"),
        (512, "512 Bytes"),
        (1023, "1023 Bytes"),
        (1024, "1.00 KB"),
        (1536, "1.50 KB"),
        (1048575, "1024.00 KB"),
        (1048576, "1.00 MB"),
        (1572864, "1.50 MB"),
        (1073741823, "1024.00 MB"),
        (1073741824, "1.00 GB"),
        (1610612736, "1.50 GB"),
    ]
)
def test_format_size(size_bytes, expected):
    assert format_size(size_bytes) == expected
