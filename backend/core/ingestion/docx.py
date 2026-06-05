import docx

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file.
    """
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
    return text
