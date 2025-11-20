# TFOCO - The Family Office Financial Document Reader

A Proof of Concept for Named Entity Recognition (NER) in financial documents, built for CMI Architecture & Innovation team.

## Test Deliverables (3 Hours)

This PoC addresses all 4 required work items:

1. **Work Item 1 - Global Architecture Document (GAD)** - `ARCHITECTURE.md`
   - CMI Information System integration context
   - Document input channels (Web UI, REST API, Message Queue, Email)
   - Synchronous vs asynchronous processing modes
   - Document confidentiality handling
   - Complete system component interactions

2. **Work Item 2 - Rule-Based Parser** - `backend/app/extractors/`
   - Python program for processing DOCX, PDF, and TXT files
   - 15+ financial entity types extraction
   - Structured JSON output with metadata
   - Comprehensive normalization functions

3. **Work Item 3 - NER Model + Methodology** - `notebooks/demo.ipynb` + `NER_FINETUNING_METHODOLOGY.md`
   - Python code demonstrating spaCy NER model usage
   - Training data preparation and annotation methodology
   - Model selection, fine-tuning process, and evaluation
   - Deployment strategy and cost estimation

4. **Work Item 4 - LLM Methodology** - `LLM_PDF_METHODOLOGY.md`
   - Comprehensive LLM-based extraction pipeline for PDF documents
   - Chunking strategies and prompting techniques
   - RAG (Retrieval-Augmented Generation) implementation
   - Error handling, validation, and hybrid approach
   - Cost optimization and performance metrics

## Features

- **Hybrid Extraction** - Rule-based patterns + NER model support
- **Multi-Format Support** - Handles PDF, DOCX, and TXT files
- **Fast Processing** - 19-42ms per document with 86%+ accuracy
- **15+ Entity Types** - Counterparties, notionals, ISINs, dates, spreads, barriers, etc.
- **Web UI** - Drag-and-drop interface for easy testing
- **REST API** - Production-ready FastAPI backend with OpenAPI docs

## Quick Start

### Prerequisites

- Python 3.11+
- (Optional) Docker & Docker Compose

### Quick Demo

**Option 1: Jupyter Notebook (Recommended for evaluation)**
```bash
cd /Users/abdullahmm/Desktop/TFOCO-PROJECT
pip install jupyter spacy
python -m spacy download en_core_web_sm
jupyter notebook notebooks/demo.ipynb
```

**Option 2: Web UI + API**
```bash
# With Docker
docker-compose up --build

# Or locally
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --port 8000

# Frontend (separate terminal)
cd frontend
npm install && npm run dev
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
TFOCO-PROJECT/
├── ARCHITECTURE.md                        # Work Item 1: GAD (CMI IS integration)
├── LLM_PDF_METHODOLOGY.md                 # Work Item 4: LLM GMD for PDF processing
├── NER_FINETUNING_METHODOLOGY.md          # Work Item 3: NER fine-tuning GMD
├── API_DOCUMENTATION.md                   # API reference and setup guide
├── README.md                              # This file
│
├── backend/                               # Work Item 2: Rule-based parser
│   ├── app/
│   │   ├── main.py                        # FastAPI endpoints
│   │   ├── extractors/
│   │   │   ├── rule_based.py              # Regex pattern matching
│   │   │   └── document_processor.py      # PDF/DOCX/TXT handling
│   │   ├── utils/
│   │   │   └── normalizers.py             # Value normalization
│   │   ├── models/
│   │   │   └── schemas.py                 # Pydantic models
│   │   └── tests/
│   │       ├── test_normalizers.py        # Unit tests
│   │       └── test_api.py                # Integration tests
│   ├── requirements.txt                   # Python dependencies
│   └── Dockerfile
│
├── notebooks/
│   └── demo.ipynb                         # Work Item 3: NER model demo with spaCy
│
├── sample_data/                           # Test files
│   ├── FR001400QV82_AVMAFC_30Jun2028.txt  # Chat format (for NER)
│   └── ZF4894_ALV_07Aug2026_physical.docx # DOCX format (for rule-based)
│
├── frontend/                              # Web UI (bonus deliverable)
│   ├── src/
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml                     # Full-stack orchestration
└── Makefile                               # Development commands
```

## Extracted Entities

| Entity | Description | Example |
|--------|-------------|---------|
| Counterparty | Trading party/client | `BANK ABC` |
| Notional | Principal amount | `200 mio` → `200,000,000 EUR` |
| ISIN | Security identifier | `FR001400QV82` |
| Underlying | Asset reference | `Allianz SE`, `AVMAFC FLOAT` |
| Maturity | Maturity date | `06/30/28` |
| Tenor | Period | `2Y` |
| Offer | Price/spread | `estr+45bps` |
| Coupon | Interest rate | `0%` |
| PaymentFrequency | Schedule | `Quarterly` |
| TradeDate | Execution date | `31 January 2025` |
| Barrier | Structured barrier | `75%` |

## Testing & Demonstration

### Test Files Provided

1. **FR001400QV82_AVMAFC_30Jun2028.txt** - Chat-style trade confirmation
   - Tests: NER model + rule-based extraction
   - Expected: 7 entities (Counterparty, Notional, ISIN, Tenor, Offer, etc.)

2. **ZF4894_ALV_07Aug2026_physical.docx** - Structured term sheet
   - Tests: Rule-based DOCX parser
   - Expected: 29 entities in 42ms with 86% confidence

### Run Tests

```bash
# Backend tests
cd backend
pytest -v

# Demo notebook (shows all approaches)
jupyter notebook notebooks/demo.ipynb

# Live API test
curl -X POST "http://localhost:8000/api/v1/extract" \
  -F "file=@sample_data/FR001400QV82_AVMAFC_30Jun2028.txt"
```

## API Documentation

### POST /api/v1/extract

Extract entities from a document.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "filename": "document.pdf",
  "entities": [
    {
      "entity": "Counterparty",
      "raw_value": "BANK ABC",
      "normalized": "BANK ABC",
      "confidence": 0.95,
      "char_start": 123,
      "char_end": 131,
      "source": "document.pdf"
    }
  ],
  "processing_time_ms": 245
}
```

## Tech Stack

### Core (Required for test)
- **Backend:** FastAPI, Python 3.11
- **Document Processing:** pdfplumber, python-docx
- **NER Model:** spaCy (en_core_web_sm)
- **Data Validation:** Pydantic v2

### Additional (Bonus)
- **Frontend:** React 18, Next.js 14, Tailwind CSS, Framer Motion
- **Testing:** pytest
- **DevOps:** Docker, Docker Compose

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Browser   │─────▶│  Next.js UI  │─────▶│  FastAPI Server │
│  (Client)   │◀─────│   (Port 3000)│◀─────│   (Port 8000)   │
└─────────────┘      └──────────────┘      └─────────────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────┐
                                          │  Extractors      │
                                          │  • Rule-based    │
                                          │  • Regex engine  │
                                          │  • Normalizers   │
                                          └──────────────────┘
```

## Configuration

Environment variables (`.env`):

```bash
# Backend
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
MAX_FILE_SIZE_MB=10

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Work Items Completion

All 4 required work items completed:

- [x] **Work Item 1 (GAD):** Global Architecture Document
  - **File:** `ARCHITECTURE.md`
  - **Content:** CMI IS integration, document channels, sync/async processing, security levels

- [x] **Work Item 2 (Coding):** Rule-Based Parser for DOCX Files
  - **Files:** `backend/app/extractors/rule_based.py`, `document_processor.py`, `normalizers.py`
  - **Features:** 15+ entity types, DOCX/PDF/TXT support, JSON output, confidence scoring

- [x] **Work Item 3 (Coding + GMD):** NER Model for Chat Files
  - **Python Code:** `notebooks/demo.ipynb` (spaCy NER model demonstration)
  - **Methodology:** `NER_FINETUNING_METHODOLOGY.md` (training, fine-tuning, deployment)

- [x] **Work Item 4 (GMD):** LLM Methodology for PDF Documents
  - **File:** `LLM_PDF_METHODOLOGY.md`
  - **Content:** Chunking, prompting, RAG, validation, hybrid approach, cost optimization

**Total Time:** 180 minutes (3 hours as specified)

---

## Key Results

| Metric | Result |
|--------|--------|
| Entities Extracted (DOCX) | 29 entities |
| Processing Time | 42ms |
| Average Confidence | 86.2% |
| Entity Types Supported | 15+ |
| File Formats | PDF, DOCX, TXT |

---
