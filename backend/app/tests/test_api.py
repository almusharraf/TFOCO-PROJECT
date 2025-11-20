"""
API integration tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import io


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestExtractEndpoint:
    """Tests for extraction endpoint"""
    
    def test_extract_txt_file(self):
        # Create sample text file
        content = """
        Counterparty: BANK ABC
        Notional: EUR 200 million
        ISIN: FR001400QV82
        Trade Date: 31 January 2025
        """
        
        files = {
            "file": ("test.txt", io.BytesIO(content.encode()), "text/plain")
        }
        
        response = client.post("/api/v1/extract", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert data["filename"] == "test.txt"
        assert data["entity_count"] > 0
        assert isinstance(data["entities"], list)
    
    def test_extract_invalid_file_type(self):
        files = {
            "file": ("test.xyz", io.BytesIO(b"content"), "application/octet-stream")
        }
        
        response = client.post("/api/v1/extract", files=files)
        assert response.status_code == 400
    
    def test_extract_empty_file(self):
        files = {
            "file": ("empty.txt", io.BytesIO(b""), "text/plain")
        }
        
        response = client.post("/api/v1/extract", files=files)
        assert response.status_code == 400

