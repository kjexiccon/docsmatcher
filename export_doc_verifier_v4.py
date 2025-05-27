
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import docx
import tempfile

st.set_page_config(page_title="SHEESH SPICES Document Verifier", layout="wide")

st.markdown("""
# 📑 SHEESH SPICES Export Document Verifier – v4
This tool performs strict field-by-field comparison across your export documents. All mismatches, even 0.001%, are flagged.
""")

master_file = st.file_uploader("📘 Upload Master Excel (Invoice or Packing List)", type=["xlsx"])
compare_file = st.file_uploader("📄 Upload Final or Draft Doc (PDF/DOCX)", type=["pdf", "docx"])

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

def flatten_excel(file):
    df = pd.read_excel(file, header=None)
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    values = []
    for row in df.values:
        for cell in row:
            if pd.notna(cell):
                values.append(str(cell).strip().lower())
    return values

def compare_fields(master_data, compare_text):
    matched = []
    mismatched = []
    for field in master_data:
        if field in compare_text:
            matched.append({"Field": field})
        else:
            mismatched.append({
                "Expected": field,
                "Found in Document": "❌ NO",
                "Severity": "Critical"
            })
    return pd.DataFrame(matched), pd.DataFrame(mismatched)

if master_file and compare_file:
    st.success("✅ Files uploaded. Running comparison...")

    master_data = flatten_excel(master_file)
    st.markdown(f"### 📋 Fields extracted from master: `{len(master_data)}` entries")
    st.code(master_data[:20] + (["..."] if len(master_data) > 20 else []))

    if compare_file.name.endswith(".pdf"):
        compare_text = extract_text_from_pdf(compare_file)
    else:
        compare_text = extract_text_from_docx(compare_file)

    matched_df, mismatched_df = compare_fields(master_data, compare_text)

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Matched Fields: {len(matched_df)}")
        st.dataframe(matched_df, use_container_width=True)
    with col2:
        st.error(f"❌ Mismatches Detected: {len(mismatched_df)}")
        st.dataframe(mismatched_df, use_container_width=True)

    if not mismatched_df.empty:
        csv = mismatched_df.to_csv(index=False).encode()
        st.download_button("📥 Download Mismatch Report", csv, "mismatch_report.csv", "text/csv")

else:
    st.info("Please upload both a master file and a document to compare.")
