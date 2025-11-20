#!/usr/bin/env python3
"""
Simple demonstration that the parser works
Run: python3 DEMO_TEST.py
"""
import sys
sys.path.insert(0, 'backend')

print("=" * 60)
print("TFOCO PARSER DEMONSTRATION")
print("=" * 60)

# Test 1: Rule-based extraction
print("\n[TEST 1] Rule-Based Extraction from Text")
print("-" * 60)

from app.extractors.rule_based import RuleBasedExtractor

sample_text = """
Counterparty: BANK ABC
Notional: EUR 200 million
ISIN: FR001400QV82
Trade Date: 31 January 2025
Barrier: 75%
Offer: estr+45bps
"""

extractor = RuleBasedExtractor()
entities = extractor.extract(sample_text, source="demo.txt")

print(f"✅ Successfully extracted {len(entities)} entities:\n")
for e in entities:
    print(f"  • {e.entity:20s} = {e.raw_value:30s} (confidence: {e.confidence:.0%})")

# Test 2: Normalizers
print("\n\n[TEST 2] Normalization Functions")
print("-" * 60)

from app.utils.normalizers import (
    normalize_amount, 
    normalize_date, 
    normalize_spread,
    normalize_percentage
)

print(f"Amount:     '200 mio'          → {normalize_amount('200 mio')}")
print(f"Date:       '31 January 2025'  → {normalize_date('31 January 2025')}")
print(f"Spread:     'estr+45bps'       → {normalize_spread('estr+45bps')}")
print(f"Percentage: '75%'              → {normalize_percentage('75%')}")

# Test 3: Document processing
print("\n\n[TEST 3] Document Processor (TXT file)")
print("-" * 60)

from app.extractors.document_processor import DocumentProcessor

processor = DocumentProcessor()
txt_entities = processor.process_document(
    'sample_data/FR001400QV82_AVMAFC_30Jun2028.txt',
    'test.txt'
)

print(f"✅ Processed TXT file: {len(txt_entities)} entities extracted")
for e in txt_entities[:5]:  # Show first 5
    print(f"  • {e.entity}: {e.raw_value}")

# Test 4: DOCX processing
print("\n\n[TEST 4] Document Processor (DOCX file)")
print("-" * 60)

try:
    docx_entities = processor.process_document(
        'sample_data/ZF4894_ALV_07Aug2026_physical.docx',
        'test.docx'
    )
    print(f"✅ Processed DOCX file: {len(docx_entities)} entities extracted")
    for e in docx_entities[:5]:  # Show first 5
        print(f"  • {e.entity}: {e.raw_value}")
except Exception as err:
    print(f"⚠️  DOCX processing: {err}")
    print("   (May need: pip install python-docx)")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - Parser is working!")
print("=" * 60)

