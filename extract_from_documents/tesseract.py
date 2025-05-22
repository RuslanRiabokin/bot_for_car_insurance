import pytesseract

from PIL import Image, ImageFilter

def foto():
    pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

    img = Image.open('passport.jpg')
    img = img.convert('L')  # в оттенки серого
    img = img.filter(ImageFilter.SHARPEN)  # увеличить резкость
    img = img.point(lambda x: 0 if x < 140 else 255)  # бинаризация

    text = pytesseract.image_to_string(img, lang='ukr+eng')
    return str(text)
print(foto())
