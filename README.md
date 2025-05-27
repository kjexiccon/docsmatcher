# Export Document Verifier

A smart document comparison tool to help exporters verify discrepancies across export documents like invoices, packing lists, COOs, fumigation, and bills of lading.

## Features
- Upload Invoice or Packing List as master reference
- Compare with Draft or Final PDF/DOCX documents
- Fuzzy matching for product names, quantities, and HS codes
- Severity tagging (Critical, Moderate)
- Auto-suggestion for corrections
- Downloadable mismatch reports

## Installation

```bash
pip install -r requirements.txt
```

## Run the App

```bash
streamlit run export_doc_verifier.py
```

## Deploy on Streamlit Cloud

1. Push these files to a GitHub repository
2. Go to https://streamlit.io/cloud
3. Connect your GitHub
4. Deploy the app from your repository