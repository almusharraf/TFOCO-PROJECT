# NER Model Fine-Tuning Methodology for Financial Entities

## Global Methodology Document (GMD)
**Work Item 3: NER Model for Chat Documents**

---

## Overview

This document explains how to fine-tune a general-purpose Named Entity Recognition (NER) model to extract financial entities from chat-style trade confirmations and unstructured text documents.

## Approach: Transfer Learning with Pre-trained NER Models

### Why Pre-trained Models?

Rather than training from scratch, we leverage transfer learning with models already trained on general entity recognition:

1. **spaCy models** (en_core_web_lg, en_core_web_trf)
2. **Hugging Face Transformers** (dslim/bert-base-NER, Jean-Baptiste/camembert-ner)
3. **Flair NER** (flair/ner-english-large)

These models understand linguistic patterns and can be fine-tuned for domain-specific entities with relatively small datasets.

---

## Step 1: Training Data Preparation

### Data Format

For spaCy fine-tuning, use the following format:

```python
TRAIN_DATA = [
    ("I'll revert regarding BANK ABC to try to do another 200 mio at 2Y", {
        "entities": [
            (21, 29, "COUNTERPARTY"),  # BANK ABC
            (52, 59, "NOTIONAL"),       # 200 mio
            (63, 65, "TENOR")           # 2Y
        ]
    }),
    ("FR001400QV82 AVMAFC FLOAT 06/30/28", {
        "entities": [
            (0, 12, "ISIN"),            # FR001400QV82
            (27, 35, "MATURITY")        # 06/30/28
        ]
    }),
    ("offer 2Y EVG estr+45bps", {
        "entities": [
            (6, 8, "TENOR"),            # 2Y
            (13, 24, "SPREAD")          # estr+45bps
        ]
    })
]
```

### Data Requirements

**Minimum Dataset Size:**
- Training: 500-1,000 annotated examples
- Validation: 100-200 examples
- Test: 100-200 examples

**Entity Coverage:**
Ensure each entity type has at least 50 examples:
- COUNTERPARTY (banks, institutions)
- NOTIONAL (amounts with units)
- ISIN (security identifiers)
- TENOR (time periods)
- SPREAD (interest rate spreads)
- BARRIER (percentage thresholds)
- UNDERLYING (asset references)
- TRADE_DATE, MATURITY, VALUATION_DATE

### Data Annotation Tools

1. **Label Studio** - Visual annotation interface
2. **Prodigy** - Active learning annotation (by spaCy team)
3. **Doccano** - Open-source text annotation
4. **Manual annotation** - Python scripts with regex pre-tagging

---

## Step 2: Model Selection

### Option A: spaCy (Recommended for Production)

**Advantages:**
- Fast inference (100-1000 docs/second)
- Small model size (50-500MB)
- Easy deployment
- Built-in tokenization for financial text

**Model Choices:**
- `en_core_web_sm` - 13MB, fast, 85% accuracy baseline
- `en_core_web_lg` - 560MB, better accuracy, 90%+ baseline
- `en_core_web_trf` - Transformer-based, 95%+ accuracy, slower

**Recommended:** Start with `en_core_web_lg` for balance of speed/accuracy.

### Option B: Hugging Face Transformers

**Advantages:**
- State-of-the-art accuracy (95-98%)
- Large pretrained model zoo
- Easy fine-tuning with Trainer API

**Model Choices:**
- `dslim/bert-base-NER` - General NER, fine-tuned BERT
- `Jean-Baptiste/roberta-large-ner-english` - RoBERTa-based
- `xlm-roberta-large-finetuned-conll03-english` - Multilingual

**Trade-off:** Higher accuracy but slower inference (10-50 docs/second).

---

## Step 3: Fine-Tuning Process

### spaCy Fine-Tuning

**1. Install Dependencies:**
```bash
pip install spacy spacy-transformers
python -m spacy download en_core_web_lg
```

**2. Create Configuration:**
```bash
python -m spacy init config config.cfg --lang en --pipeline ner --optimize efficiency
```

**3. Convert Training Data:**
```python
import spacy
from spacy.tokens import DocBin

nlp = spacy.blank("en")
doc_bin = DocBin()

for text, annotations in TRAIN_DATA:
    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annotations["entities"]:
        span = doc.char_span(start, end, label=label)
        if span:
            ents.append(span)
    doc.ents = ents
    doc_bin.add(doc)

doc_bin.to_disk("./train.spacy")
```

**4. Train Model:**
```bash
python -m spacy train config.cfg \
    --output ./output \
    --paths.train ./train.spacy \
    --paths.dev ./dev.spacy \
    --gpu-id 0
```

**5. Hyperparameters:**
- Learning rate: 0.001 (start)
- Batch size: 8-32
- Epochs: 10-30
- Dropout: 0.2-0.5
- Early stopping: patience 5

### Hugging Face Fine-Tuning

**1. Prepare Data:**
```python
from datasets import Dataset

data = {
    "tokens": [["BANK", "ABC", "200", "mio"]],
    "ner_tags": [["B-COUNTERPARTY", "I-COUNTERPARTY", "B-NOTIONAL", "I-NOTIONAL"]]
}
dataset = Dataset.from_dict(data)
```

**2. Fine-Tune:**
```python
from transformers import AutoModelForTokenClassification, Trainer, TrainingArguments

model = AutoModelForTokenClassification.from_pretrained(
    "dslim/bert-base-NER", 
    num_labels=len(label_list)
)

training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()
```

---

## Step 4: Evaluation Metrics

### Metrics to Track

**1. Entity-Level Metrics:**
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1-Score: 2 * (Precision * Recall) / (Precision + Recall)

**Target Performance:**
- F1 > 0.90 for high-confidence entities (ISIN, dates)
- F1 > 0.80 for complex entities (notionals, spreads)

**2. Token-Level Accuracy:**
- Exact match accuracy
- Partial match accuracy (for multi-word entities)

**3. Per-Entity Type Performance:**
Track F1 per entity class to identify weak spots.

### Evaluation Code:

```python
from spacy.scorer import Scorer

# Load test data
examples = []
for text, annotations in TEST_DATA:
    pred_doc = nlp(text)
    gold_doc = nlp.make_doc(text)
    gold_doc.ents = [gold_doc.char_span(s, e, label=l) 
                     for s, e, l in annotations["entities"]]
    examples.append((pred_doc, gold_doc))

# Score
scorer = Scorer()
scores = scorer.score(examples)
print(f"Precision: {scores['ents_p']:.2f}")
print(f"Recall: {scores['ents_r']:.2f}")
print(f"F1: {scores['ents_f']:.2f}")
```

---

## Step 5: Model Optimization

### Techniques for Better Performance

**1. Data Augmentation:**
- Synonym replacement (e.g., "million" → "mio", "mn")
- Entity shuffling (vary order of entities)
- Noise injection (typos, case variations)

**2. Active Learning:**
- Start with 200 examples
- Train initial model
- Use model to predict on unlabeled data
- Manually annotate low-confidence predictions
- Retrain with expanded dataset
- Repeat until target F1 reached

**3. Ensemble Methods:**
- Combine rule-based + NER model predictions
- Use rule-based for high-confidence patterns (ISINs)
- Use NER model for ambiguous cases
- Voting or weighted averaging

**4. Post-Processing:**
- Regex validation for ISINs, amounts
- Dictionary lookup for known counterparties
- Date parsing validation
- Entity consistency checks

---

## Step 6: Deployment Strategy

### Integration with Existing System

**Current Architecture:**
```
Document → Text Extraction → Rule-Based → Entities
```

**Enhanced Architecture:**
```
Document → Text Extraction → Rule-Based (high confidence)
                          ↓
                    NER Model (ambiguous)
                          ↓
                    Post-Processing → Entities
```

### Deployment Options

**Option 1: Sequential Pipeline**
1. Run rule-based extraction first
2. For low-confidence entities (< 0.7), run NER model
3. Merge results with confidence weighting

**Option 2: Parallel Voting**
1. Run both rule-based and NER in parallel
2. If both agree, high confidence
3. If they disagree, use higher confidence or ensemble

**Option 3: NER Primary**
1. Run NER model first
2. Use rules to validate/correct specific patterns
3. Combine outputs

---

## Step 7: Continuous Improvement

### Feedback Loop

1. **Production Monitoring:**
   - Track extraction accuracy on live documents
   - Log low-confidence predictions for review
   - Collect user corrections

2. **Regular Retraining:**
   - Quarterly retraining with new data
   - Incorporate user feedback into training set
   - A/B testing of new model versions

3. **Performance Tracking:**
   - Entity-level accuracy dashboard
   - Processing time metrics
   - Error pattern analysis

---

## Implementation Timeline

**Week 1: Data Collection**
- Annotate 500 training examples
- Create validation/test sets
- Validate annotation quality

**Week 2: Model Training**
- Train baseline spaCy model
- Hyperparameter tuning
- Achieve target F1 > 0.85

**Week 3: Integration**
- Integrate with existing pipeline
- Deploy to staging environment
- Performance testing

**Week 4: Production**
- Deploy to production
- Monitor performance
- Iterate based on feedback

---

## Cost Estimation

### Development Costs

| Task | Time | Cost (at $100/hr) |
|------|------|-------------------|
| Data annotation (1000 examples) | 40 hours | $4,000 |
| Model training & tuning | 20 hours | $2,000 |
| Integration & deployment | 20 hours | $2,000 |
| **Total** | **80 hours** | **$8,000** |

### Operational Costs

- **Compute:** $50-200/month (GPU for training, CPU for inference)
- **Storage:** $10/month (model artifacts, training data)
- **Monitoring:** $20/month (logging, dashboards)

**Total Operational:** ~$100-250/month

---

## Risks & Mitigation

### Risk 1: Insufficient Training Data
**Mitigation:** 
- Start with rule-based for common patterns
- Use active learning to minimize annotation effort
- Leverage data augmentation

### Risk 2: Model Drift Over Time
**Mitigation:**
- Continuous monitoring
- Regular retraining schedule
- Version control for models and data

### Risk 3: Edge Cases
**Mitigation:**
- Maintain rule-based fallback
- Human-in-the-loop for low confidence
- Gradual rollout with safety checks

---

## Conclusion

Fine-tuning NER models for financial entity extraction provides a robust solution for chat-style documents where rule-based approaches may struggle with variability. The recommended approach is:

1. **Start with spaCy** `en_core_web_lg` for balance of speed and accuracy
2. **Annotate 500-1000 examples** covering all entity types
3. **Train and evaluate** until F1 > 0.85
4. **Deploy hybrid system** combining rules + NER
5. **Monitor and retrain** quarterly

This methodology achieves production-ready NER performance while maintaining reasonable development and operational costs.

---

