import os
import yfinance as yf

class RunTimeUtils:
    def __init__(self) -> None:
        pass
    
    # Validate ticker format 
    def validate_ticker(self, v):
        v = v.strip().upper()
        if not v:           return "Ticker cannot be empty."
        if not v.isalpha(): return "Ticker must contain only letters (e.g. AAPL)."
        if len(v) > 5:      return "Ticker too long — max 5 characters."
        return ""
    
    # Validate output path and ensure parent directory exists
    def validate_path(self, v):
        v = v.strip()
        if not v: return "Path cannot be empty."
        parent = os.path.dirname(os.path.abspath(v))
        if parent and not os.path.exists(parent):
            return f"Directory does not exist: {parent}"
        return ""
    
    # Validate date in YYYY/MM/DD format with basic checks 
    def validate_date(self, v):
        v = v.strip()
        if not v:
            return "Date cannot be empty."
        parts = v.split("/")
        if len(parts) != 3:
            return "Format must be YYYY/MM/DD  (e.g. 2020/01/15)"
        year, month, day = parts
        if not (year.isdigit() and month.isdigit() and day.isdigit()):
            return "Year, month and day must all be numbers."
        y, m, d = int(year), int(month), int(day)
        if not (1900 <= y <= 2100):
            return "Year must be between 1900 and 2100."
        if not (1 <= m <= 12):
            return "Month must be between 01 and 12."
        if not (1 <= d <= 31):
            return "Day must be between 01 and 31."
        return ""
    
    # Check if ticker exists in yfinance
    def ticker_exists(self, ticker: str) -> bool:
        try:
            response = yf.Ticker(ticker).history(period="1d")
            if response.empty:
                return False
            return True
        except Exception as e:
            print(e)
            return False
