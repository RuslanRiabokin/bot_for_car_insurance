from typing import Dict

def extract_data_from_image_mock(passport_path: str, reg_path: str) -> Dict[str, str]:
    """
    Mock function to simulate data extraction from passport and registration images.

    Args:
        passport_path (str): Path to the passport image.
        reg_path (str): Path to the vehicle registration image.

    Returns:
        Dict[str, str]: Extracted mock data including full name, car number, VIN, and birth date.
    """
    return {
        "ПІБ": "Бондаренко Василий Васильевич",
        "Номер авто": "KE1234AE",
        "VIN": "VF1ABC1234567890",
        "Дата народження": "01.01.1990"
    }
