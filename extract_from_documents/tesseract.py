import os
from PIL import Image, ImageFilter, ImageOps
import pytesseract

# Попередня обробка зображення
def preprocess_image(path):
    img = Image.open(path)
    img = img.convert('L')  # відтінки сірого
    img = img.filter(ImageFilter.MedianFilter())  # зменшення шуму
    img = ImageOps.autocontrast(img)  # автоконтраст
    img = img.filter(ImageFilter.SHARPEN)  # різкість
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)  # збільшення
    img = img.point(lambda x: 0 if x < 140 else 255)  # бінаризація
    return img

# Зчитування всіх .jpg з папки, за замовчуванням - temp/
def foto_from_folder(folder_path=None):
    pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'
    config = '--psm 6'

    # Якщо шлях не вказано – встановити temp/ за замовчуванням
    if folder_path is None:
        folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'temp'))

    results = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.heic')):
            full_path = os.path.join(folder_path, filename)
            try:
                img = preprocess_image(full_path)
                text = pytesseract.image_to_string(img, lang='ukr+eng+rus', config=config)
                results.append(f"\n--- {filename} ---\n{text.strip()}")
            except Exception as e:
                results.append(f"\n--- {filename} ---\nПомилка: {str(e)}")

    return '\n'.join(results)

# Тестовий запуск напряму
if __name__ == "__main__":
    print(foto_from_folder())  # без аргументів
