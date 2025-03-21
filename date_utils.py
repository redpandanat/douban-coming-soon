# date_utils.py

import re
from datetime import datetime

def convert_date(date_str):
    current_year = datetime.now().year
    
    # Full date: YYYY年MM月DD日
    match = re.match(r"(\d{4})年(\d{2})月(\d{2})日", date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    # Year + Month: YYYY年MM月
    match = re.match(r"(\d{4})年(\d{2})月", date_str)
    if match:
        return f"{match.group(1)}-{match.group(2)}-99"
    
    # Year only: YYYY年
    match = re.match(r"(\d{4})年", date_str)
    if match:
        return f"{match.group(1)}-99-99"
    
    # Month + Day: MM月DD日 (assume current year)
    match = re.match(r"(\d{2})月(\d{2})日", date_str)
    if match:
        return f"{current_year}-{match.group(1)}-{match.group(2)}"
    
    # Month only: MM月 (assume current year)
    match = re.match(r"(\d{2})月", date_str)
    if match:
        return f"{current_year}-{match.group(1)}-99"
    
    # If format is unknown, return as is
    return date_str
