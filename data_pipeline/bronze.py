import os
import re
import datetime
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from paddleocr import PaddleOCR

# Ensure raw data folder exists
RAW_DATA_DIR = "raw_data"
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang="en")

router = APIRouter()

BANK_PATTERNS = {
    "HDFC": r"\d{2}/\d{2}/\d{4}.*?(?:Cr|Dr)",
    "SBI": r"\d{2}-\d{2}-\d{4}",
    "ICICI": r"\d{2}-\d{2}-\d{4}.*?-\d+\.\d{2}", # Negative signs for debits
    "AXIS": r"\d{2}\s+[A-Za-z]{3}\s+\d{4}"
}

def detect_bank(raw_text: str) -> str:
    """Detect the bank from raw text."""
    text_upper = raw_text.upper()
    if "HDFC" in text_upper:
        return "HDFC"
    elif "SBI" in text_upper:
        return "SBI"
    elif "ICICI" in text_upper:
        return "ICICI"
    elif "AXIS" in text_upper:
        return "AXIS"
    return "GENERIC"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Ingests raw file (PDF, PNG, JPG), saves it with a timestamped name,
    and runs PaddleOCR to extract text.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
        
    file_type = file.filename.split('.')[-1].lower()
    if file_type not in ["pdf", "png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Only PDF, PNG, and JPG are supported.")
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = file.filename.replace(" ", "_").lower()
    new_filename = f"{timestamp}_{safe_filename}"
    saved_file_path = os.path.join(RAW_DATA_DIR, new_filename)
    
    # Save original file to disk
    with open(saved_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Extract raw text with PaddleOCR
    raw_text = ""
    try:
        # PaddleOCR handles both image paths and PDF paths in recent versions
        result = ocr.ocr(saved_file_path, cls=True)
        if result:
            for res_page in result:
                if res_page is not None:
                    for line in res_page:
                        # line format: [[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], ('text', confidence)]
                        extracted_string = line[1][0]
                        raw_text += extracted_string + " \n"
    except Exception as e:
        print(f"OCR Error: {e}")
        raw_text = f"Error during OCR extraction: {str(e)}"
        
    return {
        "raw_text": raw_text.strip(),
        "file_type": file_type,
        "saved_file_path": saved_file_path
    }
