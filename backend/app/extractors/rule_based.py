"""
Rule-based entity extractor using regex patterns
"""
import re
from typing import List, Dict, Any, Pattern
from app.utils.normalizers import (
    normalize_amount,
    normalize_date,
    normalize_spread,
    normalize_percentage,
    normalize_tenor,
    normalize_isin,
    clean_text
)
from app.models.schemas import Entity


class RuleBasedExtractor:
    """Rule-based entity extraction using regex patterns"""
    
    def __init__(self):
        """Initialize extraction patterns"""
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> Dict[str, List[Pattern]]:
        """
        Build regex patterns for each entity type
        
        Returns:
            Dictionary mapping entity types to list of regex patterns
        """
        return {
            "Counterparty": [
                re.compile(r'Counterparty\s*[►▶:—–-]?\s*([A-Z][A-Z0-9 \-&]+)', re.I | re.MULTILINE),
                re.compile(r'Party\s*[AB]\s*[►▶:—–-]?\s*([A-Z][A-Z0-9 \-&]+)', re.I | re.MULTILINE),
                re.compile(r'(?:regarding|from|with)\s+([A-Z]{3,}(?:\s+[A-Z]{2,})*)\s+to', re.MULTILINE),
            ],
            
            "PartyA": [
                re.compile(r'Party\s*A\s*[►▶:—–-]?\s*([A-Z][A-Z0-9 \-&]+)', re.I | re.MULTILINE),
            ],
            
            "PartyB": [
                re.compile(r'Party\s*B\s*[►▶:—–-]?\s*([A-Z][A-Z0-9 \-&]+)', re.I | re.MULTILINE),
            ],
            
            "ISIN": [
                re.compile(r'\b([A-Z]{2}\d{9}[A-Z0-9])\b'),
            ],
            
            "Notional": [
                re.compile(r'Notional(?:\s+Amount)?\s*(?:\([A-Z]\))?\s*[►▶:—–-]?\s*([0-9\.,\s]+(?:mio|million|mn|k|b|bn)?)', re.I | re.MULTILINE),
                re.compile(r'\b((?:EUR|USD|SAR|GBP|CHF)\s*\d{1,3}(?:[,\.]\d+)?\s*(?:mio|million|mn|k|bn)?)\b', re.I),
                re.compile(r'\b(\d+\s*(?:mio|million))\s+at\s+\d+[YMD]', re.I),
            ],
            
            "TradeDate": [
                re.compile(r'Trade\s+Date\s*[►▶:—–-]?\s*([A-Za-z0-9 ,/.-]+)', re.I | re.MULTILINE),
            ],
            
            "EffectiveDate": [
                re.compile(r'Effective\s+Date\s*[►▶:—–-]?\s*([A-Za-z0-9 ,/.-]+)', re.I | re.MULTILINE),
            ],
            
            "ValuationDate": [
                re.compile(r'(?:Initial\s+)?Valuation\s+Date\s*[►▶:—–-]?\s*([A-Za-z0-9 ,/.-]+)', re.I | re.MULTILINE),
            ],
            
            "Maturity": [
                re.compile(r'(?:Termination|Maturity)\s+Date\s*[►▶:—–-]?\s*([A-Za-z0-9 ,/.-]+)', re.I | re.MULTILINE),
                re.compile(r'Maturity\s*[►▶:—–-]?\s*([A-Za-z0-9 ,/.-]+)', re.I | re.MULTILINE),
            ],
            
            "Tenor": [
                re.compile(r'\b(\d+[YMD])\s+(?:EVG|tenor|maturity)', re.I),
                re.compile(r'(?:offer|at)\s+(\d+[YMD])\b', re.I),
            ],
            
            "Underlying": [
                re.compile(r'Underlying\s*[►▶:—–-]?\s*([A-Za-z0-9 (),.\-]+(?:SE|AG|Ltd|Inc|FLOAT)?)', re.I | re.MULTILINE),
                re.compile(r'(?:ISIN|Reuters):\s*[A-Z\.]+\)?\s*([A-Za-z0-9 ,.\-]+)', re.I),
            ],
            
            "Barrier": [
                re.compile(r'Barrier\s*(?:\(B\))?\s*[►▶:—–-]?\s*([\d\.]+%?)', re.I | re.MULTILINE),
            ],
            
            "Coupon": [
                re.compile(r'Coupon\s*(?:\(C\))?\s*[►▶:—–-]?\s*([\d\.]+%?)', re.I | re.MULTILINE),
            ],
            
            "Offer": [
                re.compile(r'(?:Bid|Offer)\s*[►▶:—–-]?\s*([a-zA-Z\+\d\s]+bps|[a-zA-Z\+\-\d]+)', re.I),
                re.compile(r'\b(?:offer).*?([a-z]+\+\d+\s*bps)', re.I),
            ],
            
            "PaymentFrequency": [
                re.compile(r'Payment[- ]?Frequency\s*[►▶:—–-]?\s*([A-Za-z]+)', re.I | re.MULTILINE),
                re.compile(r'\b(Quarterly|Monthly|Annual|Semi-annual)\s+(?:interest\s+)?payment', re.I),
            ],
            
            "Exchange": [
                re.compile(r'Exchange\s*[►▶:—–-]?\s*([A-Z]+)', re.I | re.MULTILINE),
            ],
            
            "Calendar": [
                re.compile(r'(?:Business\s+Day|Calendar)\s*[►▶:—–-]?\s*([A-Z]+)', re.I | re.MULTILINE),
            ],
            
            "CalculationAgent": [
                re.compile(r'Calculation\s+Agent\s*[►▶:—–-]?\s*([A-Za-z0-9 ]+(?:and|&)?[A-Za-z0-9 ]*)', re.I | re.MULTILINE),
            ],
        }
    
    def extract(self, text: str, source: str = "document") -> List[Entity]:
        """
        Extract entities from text using rule-based patterns
        
        Args:
            text: Document text
            source: Source filename
            
        Returns:
            List of Entity objects
        """
        entities = []
        seen = set()  # Avoid duplicates
        
        # Clean text first
        text = clean_text(text)
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(text)
                
                for match in matches:
                    try:
                        raw_value = match.group(1).strip()
                        start = match.start(1)
                        end = match.end(1)
                        
                        # Skip if already extracted
                        key = (entity_type, raw_value, start)
                        if key in seen:
                            continue
                        seen.add(key)
                        
                        # Normalize value
                        normalized, unit = self._normalize_value(entity_type, raw_value)
                        
                        # Confidence scoring (simple heuristic)
                        confidence = self._calculate_confidence(entity_type, raw_value, normalized)
                        
                        entities.append(Entity(
                            entity=entity_type,
                            raw_value=raw_value,
                            normalized=normalized,
                            confidence=confidence,
                            char_start=start,
                            char_end=end,
                            source=source,
                            unit=unit
                        ))
                        
                    except (IndexError, AttributeError) as e:
                        # Skip malformed matches
                        continue
        
        return entities
    
    def _normalize_value(self, entity_type: str, raw_value: str) -> tuple:
        """
        Normalize extracted value based on entity type
        
        Args:
            entity_type: Type of entity
            raw_value: Raw extracted value
            
        Returns:
            Tuple of (normalized_value, unit)
        """
        unit = None
        
        if entity_type == "Notional":
            result = normalize_amount(raw_value)
            return result, result.get("unit")
        
        elif entity_type in ("TradeDate", "EffectiveDate", "ValuationDate", "Maturity"):
            normalized = normalize_date(raw_value)
            return normalized, None
        
        elif entity_type == "Offer":
            result = normalize_spread(raw_value)
            return result, result.get("unit")
        
        elif entity_type == "Barrier" or entity_type == "Coupon":
            result = normalize_percentage(raw_value)
            if result:
                return result, result.get("unit")
            return raw_value, None
        
        elif entity_type == "Tenor":
            result = normalize_tenor(raw_value)
            return result, result.get("unit")
        
        elif entity_type == "ISIN":
            return normalize_isin(raw_value), None
        
        else:
            # Default: return cleaned raw value
            return clean_text(raw_value), None
    
    def _calculate_confidence(self, entity_type: str, raw_value: str, normalized: Any) -> float:
        """
        Calculate confidence score for extraction
        
        Args:
            entity_type: Type of entity
            raw_value: Raw value
            normalized: Normalized value
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.85  # Base confidence
        
        # Boost confidence for well-formatted values
        if entity_type == "ISIN" and re.match(r'^[A-Z]{2}\d{9}[A-Z0-9]$', raw_value):
            confidence = 0.98
        
        elif entity_type == "Notional":
            if isinstance(normalized, dict) and normalized.get("value") is not None:
                confidence = 0.92
        
        elif entity_type in ("TradeDate", "EffectiveDate", "ValuationDate"):
            if normalized and re.match(r'\d{4}-\d{2}-\d{2}', str(normalized)):
                confidence = 0.90
        
        elif entity_type == "Counterparty":
            # Higher confidence for known bank patterns
            if any(word in raw_value.upper() for word in ['BANK', 'CAPITAL', 'SECURITIES']):
                confidence = 0.93
        
        return confidence

