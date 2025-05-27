# Export Document Verifier (Enhanced v2)

Improved smart document comparison tool with better detection of:
- Spelling and plural mismatches (e.g., Urad Gota vs Urad Gotas)
- HS code validation
- Quantity mismatches

## Features
- Upload Invoice or Packing List as master reference
- Compare against any PDF/DOCX
- Auto highlights mismatches
- Download mismatch report
- Now detects suffix/plural issues (gotas vs gota)

## Run Locally

```bash
pip install -r requirements.txt
streamlit run export_doc_verifier_v2.py
```

## Deploy to Streamlit Cloud

Main file path:
```
export_doc_verifier_v2.py
```