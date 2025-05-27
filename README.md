# SHEESH SPICES Export Document Verifier – v8

## New in v8
- UI uses expanders and color-coded alerts
- Product name, HS code, and quantity are strictly matched
- Smart alert blocks (no fuzzy match allowed)
- Uppercase normalized text ensures clarity
- Auto-rejects small spelling variations like "GOTA" vs "GOTAS"

## Run Locally
```bash
pip install -r requirements.txt
streamlit run export_doc_verifier_v8.py
```

## Streamlit Cloud
Main file path:
```
export_doc_verifier_v8.py
```