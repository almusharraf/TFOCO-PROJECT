# LLM-Based Entity Extraction Methodology for PDF Documents

**Work Item 4: Global Methodology Document (GMD)**

## Overview

This document describes how to build an LLM-based entity extraction pipeline for complex, unstructured PDF documents (term sheets, trade confirmations, agreements).

---

## 1. PDF Processing Challenges

PDFs present unique challenges:
- **Multi-column layouts** - Text extraction order issues
- **Embedded tables** - Structure lost in plain text extraction
- **Scanned documents** - Require OCR preprocessing
- **Large files** - Exceed LLM context limits (need chunking)
- **Poor formatting** - Headers, footers, page numbers add noise

---

## 2. LLM Selection

### Recommended Models

| Model | Context | Cost (Input/Output per 1M tokens) | Use Case |
|-------|---------|-----------------------------------|----------|
| **GPT-4 Turbo** | 128K | $10/$30 | Production (best balance) |
| **Claude 3 Sonnet** | 200K | $3/$15 | Cost-optimized |
| **GPT-3.5 Turbo** | 16K | $0.50/$1.50 | Development/testing |

**Recommendation:** GPT-4 Turbo for 95% accuracy at reasonable cost

---

## 3. Document Preprocessing

### Text Extraction
```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text(layout=True)  # Preserves structure
        tables = page.extract_tables()         # Extract tables separately
```

**Why pdfplumber:** Better table extraction than PyPDF2, preserves layout

### OCR for Scanned PDFs
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path(pdf_path, dpi=300)
text = pytesseract.image_to_string(images[0])
```

---

## 4. Chunking Strategy

**Problem:** PDFs often exceed LLM context limits (GPT-4: 128K tokens ≈ 100 pages)

**Solution:** Semantic chunking with overlap

```python
def chunk_document(text, max_tokens=4000, overlap=200):
    """
    Split document into chunks with overlap to prevent entity splitting
    """
    chunks = []
    words = text.split()
    
    for i in range(0, len(words), max_tokens - overlap):
        chunk = ' '.join(words[i:i + max_tokens])
        chunks.append(chunk)
    
    return chunks
```

**Key Parameters:**
- Chunk size: 4000 tokens (optimal for GPT-4)
- Overlap: 200 tokens (prevents entity splitting at boundaries)

---

## 5. Prompting Techniques

### System Prompt

```python
SYSTEM_PROMPT = """You are a financial document analyst. Extract entities with high precision.

Entity types: Counterparty, Notional, ISIN, TradeDate, Maturity, Underlying, 
Tenor, Offer/Spread, Barrier, Coupon, PaymentFrequency.

Rules:
1. Extract ONLY explicitly stated values
2. Return confidence scores (0.0-1.0)
3. Use standard formats (ISO dates, uppercase ISINs)
4. If uncertain, set confidence < 0.7
"""
```

### Few-Shot Prompting

```python
prompt = f"""
Example 1:
Text: "Trade Date: January 31, 2025. Counterparty: BANK ABC. Notional: EUR 200 million."
Output: {{"TradeDate": "2025-01-31", "Counterparty": "BANK ABC", "Notional": {{"value": 200000000, "unit": "EUR"}}}}

Example 2:
Text: "ISIN: FR001400QV82. Barrier: 75%."
Output: {{"ISIN": "FR001400QV82", "Barrier": {{"value": 75.0, "unit": "%"}}}}

Now extract from:
{chunk_text}

Return JSON only.
"""
```

### Structured Output (Function Calling)

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ],
    response_format={"type": "json_object"},  # Force JSON output
    temperature=0  # Deterministic
)

entities = json.loads(response.choices[0].message.content)
```

---

## 6. RAG (Retrieval-Augmented Generation)

**When to use RAG:**
- Very large PDFs (50+ pages)
- Multi-document analysis
- Cross-referencing between sections

**RAG Pipeline:**

```
1. Chunk document (500-token pieces)
2. Generate embeddings (OpenAI ada-002)
3. Store in vector DB (FAISS/Pinecone)
4. For extraction query:
   → Embed query
   → Retrieve top-5 relevant chunks
   → Pass to LLM with context
5. Extract entities
```

**Implementation:**

```python
import openai
import faiss

# 1. Embed chunks
embeddings = []
for chunk in chunks:
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=chunk
    )
    embeddings.append(response.data[0].embedding)

# 2. Build vector index
index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(np.array(embeddings))

# 3. Query for relevant chunks
query_embedding = openai.embeddings.create(
    model="text-embedding-ada-002",
    input="Find all trade dates"
).data[0].embedding

distances, indices = index.search(np.array([query_embedding]), k=5)
relevant_chunks = [chunks[i] for i in indices[0]]

# 4. Extract from relevant chunks only
combined = "\n\n".join(relevant_chunks)
entities = extract_with_llm(combined)
```

**Cost:** Embeddings $0.10 per 1M tokens (cheap compared to LLM calls)

---

## 7. Error Handling & Validation

### Hallucination Detection

```python
def validate_entity(entity, entity_type, value):
    """Cross-validate LLM output with rules"""
    
    if entity_type == "ISIN":
        # ISIN must be 12 chars: 2 letters + 9 digits + 1 alphanumeric
        if not re.match(r'^[A-Z]{2}\d{9}[A-Z0-9]$', value):
            return False
    
    elif entity_type == "TradeDate":
        # Must be valid ISO date
        try:
            datetime.fromisoformat(value)
        except ValueError:
            return False
    
    return True
```

### Cross-Validation with Rule-Based

```python
def hybrid_extract(text):
    """Combine rule-based + LLM for validation"""
    
    # 1. Rule-based extraction (fast, high precision)
    rule_entities = rule_based_extractor.extract(text)
    
    # 2. LLM extraction (handles ambiguous cases)
    llm_entities = llm_extractor.extract(text)
    
    # 3. Cross-validate: boost confidence if both agree
    for llm_ent in llm_entities:
        matching = [r for r in rule_entities if r['type'] == llm_ent['type']]
        if matching and matching[0]['value'] == llm_ent['value']:
            llm_ent['confidence'] = min(1.0, llm_ent['confidence'] + 0.1)
    
    return merge(rule_entities, llm_entities)
```

---

## 8. Hybrid Approach (Recommended)

```
PDF Input
    ↓
Text Extraction
    ↓
Rule-Based (fast, patterns like ISIN)
    ↓
    ├─ High confidence (>0.9) → Keep
    ├─ Medium (0.7-0.9) → Validate with LLM
    └─ Low (<0.7) → LLM extraction
           ↓
    Cross-validate
           ↓
    Final entities
```

**Benefits:**
- 60-80% cost reduction (use LLM only when needed)
- Higher accuracy (two methods agree = high confidence)
- Faster (rule-based is instant, LLM is slow)

---

## 9. Cost Optimization

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **Hybrid approach** | 60-80% | Use rules first, LLM for low confidence only |
| **Caching** | 50-70% | Cache LLM responses for identical chunks |
| **Confidence threshold** | 40-60% | Only use LLM if rule confidence < 0.7 |
| **Batch processing** | 20-30% | Process multiple docs in one API call |

**Estimated Cost:** $0.15-$0.40 per 10-page PDF with hybrid approach

---

## 10. Evaluation Metrics

### Test Dataset
- 100 manually annotated PDFs
- Ground truth labels for all entity types
- Diverse formats (term sheets, confirmations, agreements)

### Metrics

```python
def evaluate(predicted, ground_truth):
    tp = len(set(predicted) & set(ground_truth))
    fp = len(set(predicted) - set(ground_truth))
    fn = len(set(ground_truth) - set(predicted))
    
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)
    
    return {"precision": precision, "recall": recall, "f1": f1}
```

**Target Performance:**
- F1 Score: > 0.90
- Processing Time: < 30 seconds per PDF
- Cost: < $0.30 per document

---

## 11. Deployment Architecture

```
API Gateway (FastAPI)
    ↓
Job Queue (Redis)
    ↓
Worker Pool
    ├─ PDF preprocessing
    ├─ Rule-based extraction
    └─ LLM extraction (if needed)
    ↓
Result Store (PostgreSQL)
```

**Monitoring:**
- Log all LLM calls (prompt + response)
- Track costs per document
- Alert on low confidence extractions (< 0.7)
- Measure latency and throughput

---

## 12. Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Week 1** | Setup | LLM integration, basic prompts |
| **Week 2** | Optimization | Chunking, RAG, caching |
| **Week 3** | Testing | Evaluate on 100 PDFs, tune |
| **Week 4** | Production | Deploy, monitor |

---

## Summary

**Recommended Production Setup:**
1. **Primary:** Hybrid (rule-based + LLM fallback)
2. **Model:** GPT-4 Turbo
3. **Chunking:** 4000 tokens with 200-token overlap
4. **Validation:** Cross-validation + format checks
5. **Optimization:** Caching + confidence thresholds

**Expected Results:**
- Accuracy: 92-96% F1 score
- Speed: 10-30 seconds per PDF
- Cost: $0.15-$0.40 per document

**Key Success Factor:** Use LLMs selectively—not for every extraction, only when rule-based methods are uncertain.
