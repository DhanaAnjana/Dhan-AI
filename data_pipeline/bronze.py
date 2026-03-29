import os
import re
import datetime
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from paddleocr import PaddleOCR

import PyPDF2

# Ensure raw data folder exists
RAW_DATA_DIR = "raw_data"
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# Initialize OCR lazily to prevent massive memory usage on boot
_ocr = None
def get_ocr():
    global _ocr
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=True, lang="en")
    return _ocr

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
        
    # Extract raw text with smart fallback
    raw_text = ""
    try:
        if file_type == "pdf":
            # For hackathon scale, bank statements are native PDFs. This bypasses the 
            # 1.5GB RAM PaddleOCR spike which crashes Render's 512MB free tier immediately.
            reader = PyPDF2.PdfReader(saved_file_path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    raw_text += extracted + "\n"
                    
            # Auto-fallback to PaddleOCR only if it's an image-PDF with no native text
            if len(raw_text.strip()) < 50:
                print("PDF appears to be an image. Falling back to heavy OCR...")
                ocr = get_ocr()
                result = ocr.ocr(saved_file_path, cls=True)
                if result:
                    for res_page in result:
                        if res_page is not None:
                            for line in res_page:
                                raw_text += line[1][0] + " \n"
        else:
            # Images natively enforce PaddleOCR ML
            ocr = get_ocr()
            result = ocr.ocr(saved_file_path, cls=True)
            if result:
                for res_page in result:
                    if res_page is not None:
                        for line in res_page:
                            raw_text += line[1][0] + " \n"
                            
    except Exception as e:
        print(f"Extraction Error: {e}")
        raw_text = f"Error during extraction: {str(e)}"
        
    return {
        "raw_text": raw_text.strip(),
        "file_type": file_type,
        "saved_file_path": saved_file_path
    }
