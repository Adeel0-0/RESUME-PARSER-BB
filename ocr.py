# utils/ocr.py

from PIL import Image
import pytesseract

# Set the path to the installed Tesseract executable
# Use raw string (r"...") to avoid escape issues with backslashes
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(path: str) -> str:
    """
    Extracts text from an image using Tesseract OCR.

    Args:
        path (str): The file path to the image.

    Returns:
        str: The extracted text from the image.
    """
    img = Image.open(path)
    return pytesseract.image_to_string(img)
