import tempfile
import os
from datetime import datetime, timedelta
from fpdf import FPDF

FONT_PATH = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

class PDF(FPDF):
    """Custom PDF class with Unicode font and header for insurance policy."""
    def __init__(self):
        super().__init__()
        self.add_font("DejaVu", "", FONT_PATH, uni=True)
        self.set_font("DejaVu", "", 14)

    def header(self):
        """Adds a centered title at the top of the page."""
        self.set_font("DejaVu", "", 16)
        self.cell(0, 10, f"🛡️ СТРАХОВИЙ ПОЛІС № {self.policy_number}", ln=True, align="C")
        self.ln(5)

def generate_insurance_pdf(data: dict) -> str:
    """Generates a PDF file with insurance data and returns its file path."""

    today = datetime.today()
    valid_until = today + timedelta(days=365)
    policy_number = today.strftime("%Y%m%d%H%M%S")  # Унікальний номер поліса


    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    path = tmp.name
    tmp.close()


    pdf = PDF()
    pdf.policy_number = policy_number
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    pdf.ln(5)


    pdf.cell(0, 10, f"ПІБ: {data.get('ПІБ', '-')}", ln=True)
    pdf.cell(0, 10, f"Дата народження: {data.get('Дата народження', '-')}", ln=True)
    pdf.ln(5)


    pdf.cell(0, 10, f"Номер авто: {data.get('Номер авто', '-')}", ln=True)
    pdf.cell(0, 10, f"VIN: {data.get('VIN', '-')}", ln=True)
    pdf.ln(5)


    pdf.cell(0, 10, f"Тип страхування: Обов'язкове страхування цивільної відповідальності", ln=True)
    pdf.cell(0, 10, f"Період дії: {today.strftime('%d.%m.%Y')} – {valid_until.strftime('%d.%m.%Y')}", ln=True)
    pdf.cell(0, 10, f"Страхова сума: 1 130 000 грн", ln=True)
    pdf.cell(0, 10, f"Страховий тариф: 4 200 грн", ln=True)
    pdf.ln(5)


    pdf.cell(0, 10, "-" * 60, ln=True)
    pdf.cell(0, 10, "✅ Поліс видано згідно із законодавством України", ln=True)
    pdf.cell(0, 10, "📍 Страхова компанія: ТОВ \"Horns and hoofs\"", ln=True)
    pdf.cell(0, 10, f"📅 Дата формування: {today.strftime('%d.%m.%Y')}", ln=True)


    pdf.output(path)
    return path
