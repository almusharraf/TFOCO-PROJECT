"""
Unit tests for normalizers
"""
import pytest
from app.utils.normalizers import (
    normalize_amount,
    normalize_date,
    normalize_spread,
    normalize_percentage,
    normalize_tenor,
    normalize_isin
)


class TestNormalizeAmount:
    """Tests for amount normalization"""
    
    def test_millions(self):
        result = normalize_amount("200 mio")
        assert result["value"] == 200_000_000
        
    def test_with_currency(self):
        result = normalize_amount("EUR 1 million")
        assert result["value"] == 1_000_000
        assert result["unit"] == "EUR"
    
    def test_thousands(self):
        result = normalize_amount("500k")
        assert result["value"] == 500_000
    
    def test_billions(self):
        result = normalize_amount("2.5 billion")
        assert result["value"] == 2_500_000_000
    
    def test_formatted_number(self):
        result = normalize_amount("1,000,000")
        assert result["value"] == 1_000_000


class TestNormalizeDate:
    """Tests for date normalization"""
    
    def test_full_date(self):
        result = normalize_date("31 January 2025")
        assert result == "2025-01-31"
    
    def test_short_date(self):
        result = normalize_date("06/30/28")
        assert result == "2028-06-30"
    
    def test_invalid_date(self):
        result = normalize_date("not a date")
        assert result is None


class TestNormalizeSpread:
    """Tests for spread normalization"""
    
    def test_spread_with_bps(self):
        result = normalize_spread("estr+45bps")
        assert result["index"] == "ESTR"
        assert result["spread_bps"] == 45
    
    def test_spread_without_bps(self):
        result = normalize_spread("libor+100")
        assert result["index"] == "LIBOR"
        assert result["spread_bps"] == 100


class TestNormalizePercentage:
    """Tests for percentage normalization"""
    
    def test_whole_percentage(self):
        result = normalize_percentage("75%")
        assert result["value"] == 75.0
        assert result["unit"] == "%"
    
    def test_decimal_percentage(self):
        result = normalize_percentage("0.5%")
        assert result["value"] == 0.5


class TestNormalizeTenor:
    """Tests for tenor normalization"""
    
    def test_years(self):
        result = normalize_tenor("2Y")
        assert result["value"] == 2
        assert result["unit"] == "Y"
    
    def test_months(self):
        result = normalize_tenor("6M")
        assert result["value"] == 6
        assert result["unit"] == "M"


class TestNormalizeISIN:
    """Tests for ISIN normalization"""
    
    def test_uppercase(self):
        result = normalize_isin("fr001400qv82")
        assert result == "FR001400QV82"
    
    def test_trim(self):
        result = normalize_isin("  FR001400QV82  ")
        assert result == "FR001400QV82"

