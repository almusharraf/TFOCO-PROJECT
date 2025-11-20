# API Documentation

## Overview

TFOCO uses a **pure rule-based extraction system** - NO external AI APIs are required.

## Current Setup

### Backend Technology
- **Framework:** FastAPI (Python)
- **Extraction Method:** Regex pattern matching
- **Dependencies:** 
  - `pdfplumber` - PDF text extraction
  - `python-docx` - DOCX text extraction
  - `python-dateutil` - Date parsing
  - Standard Python libraries (re, json, etc.)

### API Requirements

**NO API KEYS NEEDED** - The system works completely offline using:
1. Rule-based regex patterns
2. Normalization functions
3. Document text extraction libraries

## API Endpoints

### 1. Extract Entities
```
POST /api/v1/extract
```

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF, DOCX, or TXT file, max 10MB)

**Response:**
```json
{
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
      "unit": null
    }
  ],
  "processing_time_ms": 245,
  "entity_count": 15
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -F "file=@/path/to/document.pdf"
```

### 2. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1700000000
}
```

### 3. API Documentation
```
GET /docs
```
Interactive Swagger UI documentation

---

## Future LLM Integration (Optional)

If you want to add AI-powered analysis for ambiguous entities:

### OpenAI API
```python
# Add to backend/requirements.txt
openai==1.3.0

# Set environment variable
OPENAI_API_KEY=sk-...

# Usage in code
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### Anthropic Claude API
```python
# Add to backend/requirements.txt
anthropic==0.8.0

# Set environment variable
ANTHROPIC_API_KEY=sk-ant-...

# Usage in code
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

### Example LLM Fallback Implementation

```python
# backend/app/extractors/llm_extractor.py

import os
from openai import OpenAI

class LLMExtractor:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key)
    
    def extract_ambiguous(self, text: str, entity_types: list) -> list:
        """
        Extract entities that rule-based extraction missed
        """
        prompt = f"""
        Extract the following financial entities from this text:
        Entity types: {', '.join(entity_types)}
        
        Text:
        {text}
        
        Return JSON array with: entity, raw_value, normalized, confidence
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        # Parse and return entities
        return parse_llm_response(response.choices[0].message.content)
```

---

## Environment Variables

### Current (No API Keys Required)
```bash
# Backend
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
MAX_FILE_SIZE_MB=10

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### With LLM Integration (Optional)
```bash
# Add these if using AI APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_MODEL=gpt-4
LLM_FALLBACK_ENABLED=true
```

---

## Cost Considerations

### Current System (Rule-Based)
- **Cost:** $0 per extraction
- **Speed:** ~200-500ms per document
- **Accuracy:** ~90-95% for structured documents
- **Limitations:** May miss ambiguous or non-standard formats

### With LLM Fallback (Optional)
- **OpenAI GPT-4:**
  - Input: $0.03 per 1K tokens
  - Output: $0.06 per 1K tokens
  - Typical document: ~$0.05-$0.15 per extraction
  
- **Anthropic Claude 3:**
  - Input: $0.015 per 1K tokens
  - Output: $0.075 per 1K tokens
  - Typical document: ~$0.03-$0.10 per extraction

---

## Rate Limits

### Current System
- No rate limits (self-hosted)
- Limited only by server resources

### If Adding LLM APIs
- **OpenAI:** 10,000 requests/min (paid tier)
- **Anthropic:** 4,000 requests/min (paid tier)
- Implement rate limiting in your backend

---

## Security Best Practices

### API Key Management
```bash
# Never commit API keys to git
echo "OPENAI_API_KEY=*" >> .gitignore

# Use environment variables
export OPENAI_API_KEY="sk-..."

# Or use .env file
cp .env.example .env
# Edit .env with your keys
```

### Docker Secrets
```yaml
# docker-compose.yml (for production)
services:
  backend:
    env_file:
      - .env.production
    secrets:
      - openai_api_key

secrets:
  openai_api_key:
    external: true
```

---

## Performance Optimization

### Current System
1. Compiled regex patterns (done once at startup)
2. Streaming file processing
3. Async FastAPI endpoints
4. No external API calls = fast response

### With LLM Integration
1. Cache common extractions (Redis)
2. Batch process multiple documents
3. Use async LLM clients
4. Set timeouts (30s recommended)

---

## Error Handling

### Current System Errors
- File too large (>10MB)
- Invalid file type
- Corrupted PDF/DOCX
- Empty document

### LLM Integration Errors
- API key invalid
- Rate limit exceeded
- API timeout
- Insufficient credits
- Model unavailable

---

## Testing

### Test Without API Keys
```bash
cd backend
pytest -v
```

### Test With Mock LLM
```python
# backend/app/tests/test_llm_extractor.py
from unittest.mock import Mock, patch

@patch('openai.OpenAI')
def test_llm_extraction(mock_openai):
    mock_openai.return_value.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content='{"entities": [...]}'))]
    )
    # Test extraction
```

---

## Migration Path

### Current: Pure Rule-Based
```
Document → Text Extraction → Regex Patterns → Entities
```

### Future: Hybrid Approach
```
Document → Text Extraction → Regex Patterns → Entities
                                     ↓ (if confidence < 0.7)
                              LLM Fallback → Additional Entities
```

### Implementation Steps
1. Add LLM extractor class
2. Set confidence threshold (e.g., 0.7)
3. Call LLM for low-confidence entities only
4. Merge LLM results with rule-based results
5. Add cost tracking and logging

---

## Support

For questions about:
- **Rule-based extraction:** Check `backend/app/extractors/rule_based.py`
- **Adding patterns:** Edit patterns dictionary in `RuleBasedExtractor`
- **LLM integration:** See example implementation above
- **API issues:** Check `/health` endpoint and logs

---

**Current Status:** Production-ready with rule-based extraction (NO API keys required)

**Future Enhancements:** Optional LLM fallback for improved accuracy on ambiguous documents

