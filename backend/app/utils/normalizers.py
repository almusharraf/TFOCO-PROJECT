"""
Normalizers for converting raw extracted values to structured data
"""
import re
from typing import Dict, Any, Optional
from datetime import datetime
from dateutil import parser as dateparser


def normalize_amount(raw: str) -> Dict[str, Any]:
    """
    Convert amounts like "200 mio", "1 million", "EUR 1,000,000" to integers
    
    Args:
        raw: Raw amount string
        
    Returns:
        Dict with 'value' (int), 'unit' (str), 'raw' (str)
        
    Examples:
        "200 mio" -> {"value": 200000000, "unit": None, "raw": "200 mio"}
        "EUR 1 million" -> {"value": 1000000, "unit": "EUR", "raw": "EUR 1 million"}
    """
    s = raw.strip().lower().replace(',', '').replace('\xa0', ' ')
    unit = None
    
    # Detect currency
    currencies = ['eur', 'usd', 'gbp', 'sar', 'chf', 'jpy', 'inr']
    for curr in currencies:
        if curr in s:
            unit = curr.upper()
            break
    
    # Handle magnitude multipliers
    magnitude_map = {
        'mio': 1_000_000,
        'million': 1_000_000,
        'millions': 1_000_000,
        'mn': 1_000_000,
        'm': 1_000_000,
        'billion': 1_000_000_000,
        'billions': 1_000_000_000,
        'bn': 1_000_000_000,
        'b': 1_000_000_000,
        'thousand': 1_000,
        'k': 1_000,
    }
    
    # Extract number and magnitude
    pattern = r'([\d\.]+)\s*(' + '|'.join(magnitude_map.keys()) + r')?\b'
    match = re.search(pattern, s)
    
    if match:
        try:
            num = float(match.group(1))
            magnitude = match.group(2)
            
            if magnitude and magnitude in magnitude_map:
                factor = magnitude_map[magnitude]
            else:
                factor = 1
            
            value = int(num * factor)
            
            return {
                "value": value,
                "unit": unit,
                "raw": raw
            }
        except (ValueError, TypeError):
            pass
    
    # Fallback: try to find any number
    num_match = re.search(r'[\d,\.]+', raw)
    if num_match:
        try:
            value = int(float(num_match.group().replace(',', '')))
            return {"value": value, "unit": unit, "raw": raw}
        except (ValueError, TypeError):
            pass
    
    return {"value": None, "unit": unit, "raw": raw}


def normalize_date(raw: str) -> Optional[str]:
    """
    Convert date strings to ISO 8601 format (YYYY-MM-DD)
    
    Args:
        raw: Raw date string
        
    Returns:
        ISO formatted date string or None if parsing fails
        
    Examples:
        "31 January 2025" -> "2025-01-31"
        "06/30/28" -> "2028-06-30"
    """
    try:
        # Handle MM/DD/YY format
        if re.match(r'\d{2}/\d{2}/\d{2}', raw):
            dt = datetime.strptime(raw, "%m/%d/%y")
        else:
            dt = dateparser.parse(raw, dayfirst=False)
        
        if dt:
            return dt.date().isoformat()
    except (ValueError, TypeError, AttributeError):
        pass
    
    return None


def normalize_spread(raw: str) -> Dict[str, Any]:
    """
    Parse spread/rate strings like "estr+45bps" into structured data
    
    Args:
        raw: Raw spread string
        
    Returns:
        Dict with 'index', 'spread_bps', and 'raw'
        
    Examples:
        "estr+45bps" -> {"index": "ESTR", "spread_bps": 45, "raw": "estr+45bps"}
        "LIBOR + 100" -> {"index": "LIBOR", "spread_bps": 100, "raw": "LIBOR + 100"}
    """
    s = raw.replace(' ', '').lower()
    
    # Pattern: index+numbersbps or index+numbers
    patterns = [
        r'([a-z]+)\+(\d+)\s*bps',
        r'([a-z]+)\+(\d+)',
        r'([a-z]+)-(\d+)\s*bps',
        r'([a-z]+)-(\d+)',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, s)
        if match:
            index = match.group(1).upper()
            spread = int(match.group(2))
            
            # Handle negative spread for minus sign
            if '-' in pattern:
                spread = -spread
            
            return {
                "index": index,
                "spread_bps": spread,
                "raw": raw
            }
    
    return {"raw": raw}


def normalize_percentage(raw: str) -> Optional[Dict[str, Any]]:
    """
    Extract percentage values
    
    Args:
        raw: Raw percentage string
        
    Returns:
        Dict with 'value' and 'unit' ('%')
        
    Examples:
        "75%" -> {"value": 75.0, "unit": "%"}
        "0.5%" -> {"value": 0.5, "unit": "%"}
    """
    s = raw.strip().replace('%', '').replace(',', '')
    
    try:
        value = float(s)
        return {
            "value": value,
            "unit": "%",
            "raw": raw
        }
    except (ValueError, TypeError):
        pass
    
    return None


def normalize_tenor(raw: str) -> Dict[str, Any]:
    """
    Normalize tenor strings like "2Y", "6M" to structured format
    
    Args:
        raw: Raw tenor string
        
    Returns:
        Dict with 'value', 'unit', and 'raw'
        
    Examples:
        "2Y" -> {"value": 2, "unit": "Y", "raw": "2Y"}
        "6M" -> {"value": 6, "unit": "M", "raw": "6M"}
    """
    s = raw.strip().upper()
    
    match = re.match(r'(\d+)\s*([YMWD])', s)
    if match:
        value = int(match.group(1))
        unit_map = {'Y': 'years', 'M': 'months', 'W': 'weeks', 'D': 'days'}
        unit = match.group(2)
        
        return {
            "value": value,
            "unit": unit,
            "unit_full": unit_map.get(unit, unit),
            "raw": raw
        }
    
    return {"raw": raw}


def normalize_isin(raw: str) -> str:
    """
    Validate and normalize ISIN codes
    
    Args:
        raw: Raw ISIN string
        
    Returns:
        Normalized ISIN (uppercase, trimmed)
    """
    return raw.strip().upper()


def clean_text(text: str) -> str:
    """
    Clean extracted text (remove extra whitespace, normalize characters)
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    # Replace non-breaking spaces and multiple spaces
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

