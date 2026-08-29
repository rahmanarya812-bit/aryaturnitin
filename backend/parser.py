import os
import re
import io

def extract_text_from_txt_bytes(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")

def extract_text_from_pdf_bytes(content: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF bytes: {e}")
        return ""

def extract_text_from_docx_bytes(content: bytes) -> str:
    try:
        import docx
        doc = docx.Document(io.BytesIO(content))
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error reading DOCX bytes: {e}")
        return ""

def extract_text_from_bytes(content: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf_bytes(content)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx_bytes(content)
    else:
        return extract_text_from_txt_bytes(content)

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    with open(file_path, "rb") as f:
        content = f.read()
    return extract_text_from_bytes(content, file_path)
