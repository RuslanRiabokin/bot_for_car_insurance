import os
from fpdf import FPDF
from datetime import datetime
from services.mindee_service import extract_data_from_image_mock

def generate_policy_pdf(passport_path: str, reg_path: str, output_path: str) -> str:
    """
        Generates a car insurance policy in PDF format based on provided document images.

        Args:
            passport_path (str): Path to the passport image file.
            reg_path (str): Path to the vehicle registration image file.
            output_path (str): Path where the generated PDF will be saved.

        Returns:
            str: Path to the generated PDF file.
        """
    data = extract_data_from_image_mock(passport_path, reg_path)

    text = f"""
Страховий поліс №123456

Страхувальник: {data['ПІБ']}
Дата народження: {data['Дата народження']}

Дані про автомобіль:
Номер авто: {data['Номер авто']}
VIN: {data['VIN']}

Цим підтверджується, що транспортний засіб застрахований відповідно до умов договору.

Дата: {datetime.now().strftime('%d.%m.%Y')}
Підпис страхувальника: ___________________
""".strip()


    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    pdf = FPDF()
    pdf.add_page()

    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
    else:
        pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, text)
    pdf.output(output_path)

    return output_path
