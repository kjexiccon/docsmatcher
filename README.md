# SHEESH SPICES Export Document Verifier – v8c

## New in v8c
- Auto-detects headers like 'Item', 'Qty', 'HS' from Excel
- Gives immediate error if products not found
- Cleaner layout with expandable result blocks
- Smart alerts like:
  - ✅ All match for URAD GOTAS
  - ❌ Product mismatch in PHYTO

## Run Locally
```bash
pip install -r requirements.txt
streamlit run export_doc_verifier_v8c.py
```

## Streamlit Cloud Main File Path
```
export_doc_verifier_v8c.py
```