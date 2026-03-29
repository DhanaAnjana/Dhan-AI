import re
from typing import List, Dict, Any
from datetime import datetime

BANK_EXTRACTION_PATTERNS = {
    # HDFC uses DD/MM/YYYY with Cr/Dr suffixes
    "HDFC": r"(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<merchant>(?:(?!\d{2}/\d{2}/\d{4}).)+?)\s+(?P<amount>[\d,]+\.\d{2})\s*(?P<type>Cr|Dr)",
    
    # SBI uses DD-MM-YYYY
    "SBI": r"(?P<date>\d{2}-\d{2}-\d{4})\s+(?P<merchant>(?:(?!\d{2}-\d{2}-\d{4}).)+?)\s+(?P<amount>[\d,]+\.\d{2})\s*(?P<type>Cr|Dr)?",
    
    # ICICI uses DD-MM-YYYY with negative signs for debits (and no explicit cr/dr)
    "ICICI": r"(?P<date>\d{2}-\d{2}-\d{4})\s+(?P<merchant>(?:(?!\d{2}-\d{2}-\d{4}).)+?)\s+(?P<amount>-?[\d,]+\.\d{2})",
    
    # AXIS uses DD Mon YYYY format
    "AXIS": r"(?P<date>\d{2}\s+[A-Za-z]{3}\s+\d{4})\s+(?P<merchant>(?:(?!\d{2}\s+[A-Za-z]{3}\s+\d{4}).)+?)\s+(?P<amount>[\d,]+\.\d{2})\s*(?P<type>Cr|Dr)?",
    
    # GENERIC uses standard formats looking for a word and number
    "GENERIC": r"(?P<date>\d{2}[/-]\d{2}[/-]\d{4}|\d{2}\s+[A-Za-z]{3}\s+\d{4})\s+(?P<merchant>(?:(?!\d{2}[/-]\d{2}[/-]\d{4}|\d{2}\s+[A-Za-z]{3}\s+\d{4}).)+?)\s+(?P<amount>-?[\d,]+\.\d{2})\s*(?P<type>Cr|Dr)?"
}

def standardise_date(date_str: str) -> str:
    """
    Parses common date strings and returns YYYY-MM-DD format.
    If none match, returns original.
    """
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%d %b %Y", "%d-%b-%Y"]
    # Provide minor sanitization
    date_str = date_str.strip()
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
            
    return date_str

def clean_merchant(merchant_name: str) -> str:
    """
    Strips out everything after asterisks, hyphens, or underscores 
    followed by alphanumeric noise. Also removes UPI prefixes. Title-cases result.
    """
    if not merchant_name:
        return ""
        
    # Remove UPI prefixes
    cleaned = re.sub(r'^(?i:UPI|IMPS|NEFT|RTGS)[/-]', '', merchant_name)
    
    # Split by any punctuation that typically divides Merchant and Noisy IDs (*, -, _)
    parts = re.split(r'[*_\-]', cleaned)
    
    if parts:
        # The first part usually holds the cleanest merchant name
        return parts[0].strip().title()
        
    return cleaned.strip().title()

def process_silver(raw_text: str, bank_name: str) -> List[Dict[str, Any]]:
    """
    Extracts dates, merchants, amounts, and types from raw text and cleans them.
    Output is in standard JSON format ready for AgentState: clean_transactions.
    """
    # Flatten the text to handle line breaks between columns easily
    flattened_text = raw_text.replace('\n', ' ')
    
    pattern_str = BANK_EXTRACTION_PATTERNS.get(bank_name, BANK_EXTRACTION_PATTERNS["GENERIC"])
    
    clean_transactions = []
    
    for match in re.finditer(pattern_str, flattened_text, re.IGNORECASE):
        groups = match.groupdict()
        
        date_raw = groups.get("date", "")
        merchant_raw = groups.get("merchant", "")
        amount_raw = groups.get("amount", "")
        type_raw = groups.get("type", "")
        
        if not amount_raw:
            continue
            
        amount_val = 0.0
        txn_type = "debit" # default assumption
        
        try:
            # Handle comma within amounts, usually for larger numbers e.g. 10,000.00
            amt_str = amount_raw.replace(',', '')
            if amt_str.startswith('-'):
                txn_type = "debit"
                amount_val = float(amt_str[1:])
            else:
                amount_val = float(amt_str)
                # Parse available type indicators
                if type_raw:
                    if type_raw.lower() == "cr":
                        txn_type = "credit"
                    elif type_raw.lower() == "dr":
                        txn_type = "debit"
                elif bank_name == "ICICI":
                    # ICICI positive implies credit
                    txn_type = "credit"
        except ValueError:
            continue
            
        clean_transactions.append({
            "date": standardise_date(date_raw),
            "merchant": clean_merchant(merchant_raw),
            "amount": amount_val,
            "type": txn_type
        })
        
    return clean_transactions
