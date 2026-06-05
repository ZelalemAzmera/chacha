from core.ocr import extract_text_from_image

def extract_text_from_material_image(file_path: str) -> str:
    """
    Extracts text from an image material (like a photo of a textbook page).
    """
    return extract_text_from_image(file_path, is_question=False)
