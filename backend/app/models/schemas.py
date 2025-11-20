"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from enum import Enum


class EntityType(str, Enum):
    """Supported entity types"""
    COUNTERPARTY = "Counterparty"
    NOTIONAL = "Notional"
    ISIN = "ISIN"
    UNDERLYING = "Underlying"
    MATURITY = "Maturity"
    TENOR = "Tenor"
    OFFER = "Offer"
    COUPON = "Coupon"
    PAYMENT_FREQUENCY = "PaymentFrequency"
    TRADE_DATE = "TradeDate"
    EFFECTIVE_DATE = "EffectiveDate"
    VALUATION_DATE = "ValuationDate"
    BARRIER = "Barrier"
    CALENDAR = "Calendar"
    CALCULATION_AGENT = "CalculationAgent"
    PARTY_A = "PartyA"
    PARTY_B = "PartyB"
    EXCHANGE = "Exchange"


class Entity(BaseModel):
    """Extracted entity model"""
    entity: str = Field(..., description="Entity type")
    raw_value: str = Field(..., description="Raw extracted value from document")
    normalized: Optional[Any] = Field(None, description="Normalized/structured value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score")
    char_start: int = Field(..., description="Character offset start position")
    char_end: int = Field(..., description="Character offset end position")
    source: str = Field(..., description="Source file name")
    unit: Optional[str] = Field(None, description="Unit if applicable (EUR, %, etc)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity": "Counterparty",
                "raw_value": "BANK ABC",
                "normalized": "BANK ABC",
                "confidence": 0.95,
                "char_start": 123,
                "char_end": 131,
                "source": "document.pdf",
                "unit": None
            }
        }


class ExtractionResponse(BaseModel):
    """API response for entity extraction"""
    filename: str = Field(..., description="Uploaded filename")
    file_size: int = Field(..., description="File size in bytes")
    entities: List[Entity] = Field(..., description="List of extracted entities")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    entity_count: int = Field(..., description="Total number of entities extracted")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "document.pdf",
                "file_size": 12345,
                "entities": [
                    {
                        "entity": "Counterparty",
                        "raw_value": "BANK ABC",
                        "normalized": "BANK ABC",
                        "confidence": 0.95,
                        "char_start": 123,
                        "char_end": 131,
                        "source": "document.pdf",
                        "unit": None
                    }
                ],
                "processing_time_ms": 245,
                "entity_count": 1
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: int = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": 1700000000
            }
        }

