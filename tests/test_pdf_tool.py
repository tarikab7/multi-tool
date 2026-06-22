import os
import pytest
import pytest_asyncio
from PIL import Image
from tools.pdf_tool import compile_images_to_pdf, extract_pdf_to_images, run

@pytest.fixture
def dummy_images_folder(tmp_path):
    img_folder = tmp_path / "images"
    img_folder.mkdir()

    # Create two dummy images
    img1 = Image.new("RGB", (100, 100), color="red")
    img1.save(img_folder / "img1.jpg")

    img2 = Image.new("RGB", (100, 100), color="blue")
    img2.save(img_folder / "img2.jpg")

    return str(img_folder)

@pytest.fixture
def empty_folder(tmp_path):
    folder = tmp_path / "empty"
    folder.mkdir()
    return str(folder)

def test_compile_images_to_pdf_success(dummy_images_folder, tmp_path):
    output_pdf = str(tmp_path / "output.pdf")
    success, msg = compile_images_to_pdf(dummy_images_folder, output_pdf)

    assert success is True
    assert "Successfully merged" in msg
    assert os.path.exists(output_pdf)

def test_compile_images_to_pdf_no_images(empty_folder, tmp_path):
    output_pdf = str(tmp_path / "output.pdf")
    success, msg = compile_images_to_pdf(empty_folder, output_pdf)

    assert success is False
    assert "No images found in folder" in msg

def test_extract_pdf_to_images_success(dummy_images_folder, tmp_path, mocker):
    # First create a PDF
    output_pdf = str(tmp_path / "output.pdf")
    compile_images_to_pdf(dummy_images_folder, output_pdf)

    # Extract
    extract_folder = str(tmp_path / "extracted")

    # Mock Image.open to avoid Ghostscript dependency
    mock_img = mocker.MagicMock()
    mock_img.__enter__.return_value = mock_img

    # Simulate 2 pages
    mock_page_img = mocker.MagicMock()
    mock_img.convert.return_value = mock_page_img

    def mock_seek(page):
        if page >= 2:
            raise EOFError()
    mock_img.seek.side_effect = mock_seek

    mocker.patch("tools.pdf_tool.Image.open", return_value=mock_img)

    success, msg = extract_pdf_to_images(output_pdf, extract_folder)

    assert success is True
    assert "Successfully extracted 2" in msg
    assert os.path.exists(extract_folder)
    assert mock_page_img.save.call_count == 2

def test_extract_pdf_to_images_failure(tmp_path):
    # Pass a non-existent file or a text file instead of PDF
    bad_pdf = str(tmp_path / "bad.pdf")
    with open(bad_pdf, "w") as f:
        f.write("not a pdf")

    extract_folder = str(tmp_path / "extracted")
    success, msg = extract_pdf_to_images(bad_pdf, extract_folder)

    assert success is False
    assert "Failed extracting PDF pages" in msg

@pytest.mark.asyncio
async def test_run_images_to_pdf_success(dummy_images_folder, tmp_path):
    output_pdf = str(tmp_path / "output.pdf")
    params = {
        "mode": "images_to_pdf",
        "input_path": dummy_images_folder,
        "output_path": output_pdf
    }

    results = [res async for res in run(params)]

    # Expected events
    assert results[0].get("type") == "log"
    assert "Gathering images from" in results[0].get("message")

    assert results[1].get("type") == "progress"
    assert results[1].get("percent") == 100.0

    assert results[2].get("type") == "log"
    assert "Successfully merged" in results[2].get("message")

    assert results[3].get("type") == "success"
    assert results[3].get("message") == "PDF created successfully."

@pytest.mark.asyncio
async def test_run_pdf_to_images_success(dummy_images_folder, tmp_path, mocker):
    # First create a PDF
    output_pdf = str(tmp_path / "output.pdf")
    compile_images_to_pdf(dummy_images_folder, output_pdf)

    extract_folder = str(tmp_path / "extracted")
    params = {
        "mode": "pdf_to_images",
        "input_path": output_pdf,
        "output_path": extract_folder
    }

    # Mock extract_pdf_to_images so we don't need Ghostscript
    mocker.patch("tools.pdf_tool.extract_pdf_to_images", return_value=(True, "Successfully extracted 2 page(s)"))

    results = [res async for res in run(params)]

    assert results[0].get("type") == "log"
    assert "Extracting pages from" in results[0].get("message")

    assert results[1].get("type") == "progress"
    assert results[1].get("percent") == 100.0

    assert results[2].get("type") == "log"
    assert "Successfully extracted" in results[2].get("message")

    assert results[3].get("type") == "success"
    assert results[3].get("message") == "PDF pages extracted successfully."

@pytest.mark.asyncio
async def test_run_missing_inputs():
    params = {}
    results = [res async for res in run(params)]

    assert len(results) == 1
    assert results[0].get("type") == "error"
    assert "Both input and output paths are required." in results[0].get("message")

@pytest.mark.asyncio
async def test_run_invalid_images_to_pdf_folder(tmp_path):
    invalid_folder = str(tmp_path / "non_existent")
    output_pdf = str(tmp_path / "output.pdf")
    params = {
        "mode": "images_to_pdf",
        "input_path": invalid_folder,
        "output_path": output_pdf
    }

    results = [res async for res in run(params)]
    assert len(results) == 1
    assert results[0].get("type") == "error"
    assert "does not exist" in results[0].get("message")

@pytest.mark.asyncio
async def test_run_invalid_images_to_pdf_extension(dummy_images_folder, tmp_path):
    output_txt = str(tmp_path / "output.txt")
    params = {
        "mode": "images_to_pdf",
        "input_path": dummy_images_folder,
        "output_path": output_txt
    }

    results = [res async for res in run(params)]
    assert len(results) == 1
    assert results[0].get("type") == "error"
    assert "must end with '.pdf'" in results[0].get("message")
