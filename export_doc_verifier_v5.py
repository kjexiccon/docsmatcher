
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import docx
import tempfile

st.set_page_config(page_title="SHEESH SPICES Document Verifier – v5", layout="wide")
st.title("📋 SHEESH SPICES Document Verifier – v5 (Strict Row Comparison)")
st.markdown("This version enforces **strict field-by-field and row-based comparison**. No fuzzy matching is used. Even small spelling errors are flagged.")

master_file = st.file_uploader("📘 Upload Master Excel (Structured Line Items)", type=["xlsx"])
compare_file = st.file_uploader("📄 Upload Final/Draft Document (PDF/DOCX)", type=["pdf", "docx"])

def extract_text_from_pdf(file):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp.flush()
        doc = fitz.open(tmp.name)
        for page in doc:
            text += page.get_text()
    return text.lower()

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.lower()

def compare_structured_rows(df, doc_text):
    matched_rows = []
    mismatched_rows = []

    for idx, row in df.iterrows():
        row_pass = True
        mismatch_reasons = []

        for col in df.columns:
            val = str(row[col]).strip().lower()
            if val and val not in doc_text:
                row_pass = False
                mismatch_reasons.append(f"{col}: '{val}' not found")

        if row_pass:
            matched_rows.append(row.to_dict())
        else:
            mismatched_rows.append({
                "Row": idx + 2,
                "Mismatch Fields": "; ".join(mismatch_reasons),
                "Row Content": str(row.to_dict())
            })

    return pd.DataFrame(matched_rows), pd.DataFrame(mismatched_rows)

if master_file and compare_file:
    st.success("✅ Files uploaded. Processing with strict row-level logic...")

    df = pd.read_excel(master_file).fillna("").astype(str)
    st.markdown("### 📋 Structured Master Data")
    st.dataframe(df.head(), use_container_width=True)

    if compare_file.name.endswith(".pdf"):
        compare_text = extract_text_from_pdf(compare_file)
    else:
        compare_text = extract_text_from_docx(compare_file)

    matched_df, mismatched_df = compare_structured_rows(df, compare_text)

    st.markdown("## ✅ Matched Rows")
    st.dataframe(matched_df, use_container_width=True)

    st.markdown("## ❌ Mismatched Rows")
    st.dataframe(mismatched_df, use_container_width=True)

    if not mismatched_df.empty:
        csv = mismatched_df.to_csv(index=False).encode()
        st.download_button("📥 Download Mismatch Report", csv, "mismatch_report.csv", "text/csv")

else:
    st.info("Please upload a structured Excel file and a document to compare.")
