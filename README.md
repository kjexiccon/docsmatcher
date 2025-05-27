# SHEESH SPICES Export Document Verifier – v5

## Features
- Strict row-by-row matching (no fuzzy logic)
- Product name, HSN, Qty, etc. must match exactly
- Flags minor spelling or punctuation errors
- Mismatch reasons are shown per row
- Supports DOCX and PDF for comparison
- Mismatch report downloadable as CSV

## How to Run

```bash
pip install -r requirements.txt
streamlit run export_doc_verifier_v5.py
```

## Deploy on Streamlit Cloud
Main file path:
```
export_doc_verifier_v5.py
```