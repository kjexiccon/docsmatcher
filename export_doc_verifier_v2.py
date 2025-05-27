
import streamlit as st
import pandas as pd
import difflib
from rapidfuzz import fuzz
import tempfile
import fitz  # PyMuPDF for PDF support
import docx
import re

st.set_page_config(page_title="Export Document Verifier", layout="wide")
st.title("📦 Export Document Verifier")
st.markdown("Upload your **Invoice / Packing List (master)** and any draft/final doc to compare key fields.")

# Upload master data files
master_file = st.file_uploader("Upload Master File (Invoice or Packing List) [.xlsx]", type=["xlsx"])
compare_file = st.file_uploader("Upload Document to Compare [.pdf, .docx]", type=["pdf", "docx"])

def extract_text_from_pdf(file):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    doc = fitz.open(tmp_path)
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file):
    text = ""
    doc = docx.Document(file)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def clean_term(term):
    term = str(term).strip().lower()
    term = re.sub(r"\bes\b|\bs\b|\bdal\b|\bsplit\b|\bwhole\b", "", term)
    return term.strip()

def fuzzy_match_strict(val1, val2):
    # Enhanced match with suffix cleaning
    clean1 = clean_term(val1)
    clean2 = clean_term(val2)
    return fuzz.token_sort_ratio(clean1, clean2)

def highlight_mismatches(master_df, compare_text, threshold=95):
    mismatches = []
    for idx, row in master_df.iterrows():
        product = str(row.get("Product", ""))
        qty = str(row.get("Quantity", ""))
        hs = str(row.get("HS Code", ""))

        score_product = fuzzy_match_strict(product, compare_text)
        score_qty = fuzz.token_sort_ratio(qty, compare_text)
        score_hs = fuzz.token_sort_ratio(hs, compare_text)

        if score_product < threshold:
            mismatches.append({
                "Field": "Product Name",
                "Value": product,
                "Match %": score_product,
                "Severity": "Moderate" if score_product >= 80 else "Critical",
                "Suggested Fix": "Spelling or suffix mismatch (e.g., plural/singular)"
            })
        if score_qty < 100:
            mismatches.append({
                "Field": "Quantity",
                "Value": qty,
                "Match %": score_qty,
                "Severity": "Critical",
                "Suggested Fix": "Must match exactly"
            })
        if score_hs < threshold:
            mismatches.append({
                "Field": "HS Code",
                "Value": hs,
                "Match %": score_hs,
                "Severity": "Critical",
                "Suggested Fix": "Use correct HS code"
            })
    return pd.DataFrame(mismatches)

if master_file and compare_file:
    st.success("Both files uploaded. Processing...")

    master_df = pd.read_excel(master_file)
    st.markdown("### 📄 Master Data (Invoice or Packing List)")
    st.dataframe(master_df)

    if compare_file.name.endswith(".pdf"):
        compare_text = extract_text_from_pdf(compare_file)
    else:
        compare_text = extract_text_from_docx(compare_file)

    st.markdown("### 🔍 Document Text Preview (Comparison Target)")
    with st.expander("Show Extracted Text"):
        st.text(compare_text[:2000] + "...")

    results_df = highlight_mismatches(master_df, compare_text)

    if results_df.empty:
        st.success("✅ No mismatches found!")
    else:
        st.error("❌ Mismatches detected:")
        st.dataframe(results_df, use_container_width=True)
        csv = results_df.to_csv(index=False).encode()
        st.download_button("📥 Download Mismatch Report", csv, "mismatch_report.csv", "text/csv")

else:
    st.info("Please upload both master and comparison files to begin.")
