from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Use just the filename if the image is in the same directory
img = Image.open("tempef3d095e5ebdf5bae6335a4cb4148597.jpg")
text = pytesseract.image_to_string(img)
print(text)
