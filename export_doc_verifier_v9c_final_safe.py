
import streamlit as st
import pandas as pd
import pdfplumber
import docx
import tempfile
from fpdf import FPDF

st.set_page_config(page_title="SHEESH SPICES Verifier – v9c FINAL SAFE", layout="wide")
st.title("📦 SHEESH SPICES Export Document Verifier – v9c")

st.markdown("Final version: Accurate, fast, zero-tolerance document checker for exports.")
st.write("✅ App loaded successfully. Upload your files to begin.")

master_file = st.sidebar.file_uploader("Upload Primary Excel (Invoice or Packing List)", type=["xlsx"])
compare_files = st.sidebar.file_uploader("Upload Other Docs (PDF, DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

def extract_text(file):
    if file.name.endswith(".pdf"):
        text = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            tmp.flush()
            with pdfplumber.open(tmp.name) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        return text.upper()
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs]).upper()
    return ""

def extract_invoice_data(df):
    headers = {"Exporter": "", "Buyer": "", "Invoice No": "", "Date": "", "POL": "", "POD": "",
               "Total Box": "", "Total NW": "", "Total GW": ""}
    for row in df.iloc[:20].astype(str).values.flatten():
        r = row.upper()
        if "EXPORTER" in r:
            headers["Exporter"] = r.strip()
        if "BUYER" in r:
            headers["Buyer"] = r.strip()
        if "CI/EXP" in r or "INVOICE" in r:
            headers["Invoice No"] = r.strip()
        if any(x in r for x in ["2024", "2025"]):
            headers["Date"] = r.strip()
        if "PORT OF LOADING" in r:
            headers["POL"] = r.strip()
        if "PORT OF DISCHARGE" in r or "FINAL DESTINATION" in r:
            headers["POD"] = r.strip()
        if "TOTAL BOX" in r:
            headers["Total Box"] = r.strip()
        if "TOTAL NET" in r:
            headers["Total NW"] = r.strip()
        if "TOTAL GROSS" in r:
            headers["Total GW"] = r.strip()
    return headers

def extract_product_rows(df):
    product_data = []
    try:
        sub_df = df.iloc[23:60].fillna("").astype(str)
        for i, row in sub_df.iterrows():
            name = row[2].strip().upper()
            hscode = row[9].strip()
            qty = row[14].strip()
            if name and hscode and qty:
                product_data.append({"Product": name, "HS Code": hscode, "Quantity": qty})
    except:
        pass
    return product_data

def compare_text(val, doc_text):
    return val and val in doc_text

def match_fields_against_docs(fields, docs):
    result = []
    for label, value in fields.items():
        for docname, doctx in docs.items():
            if not compare_text(value, doctx):
                result.append({"Field": label, "Expected": value, "Found in": docname, "Match": "❌"})
            else:
                result.append({"Field": label, "Expected": value, "Found in": docname, "Match": "✅"})
    return result

def match_products_against_docs(products, docs):
    rows = []
    for prod in products:
        for docname, doctx in docs.items():
            checks = {
                "PNM": not compare_text(prod["Product"], doctx),
                "HSC": not compare_text(prod["HS Code"], doctx),
                "QTY": not compare_text(prod["Quantity"], doctx),
            }
            issues = [k for k, v in checks.items() if v]
            rows.append({
                "Product": prod["Product"],
                "Doc": docname,
                "Status": "✅" if not issues else "❌ " + ", ".join(issues)
            })
    return rows

def export_pdf(df_rows):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Document Comparison Report", ln=True, align="C")
    pdf.ln(5)
    for _, row in df_rows.iterrows():
        raw = f"{row.get('Field', row.get('Product', ''))} → {row['Match' if 'Match' in row else 'Status']} in {row['Found in' if 'Found in' in row else 'Doc']}"
        clean = raw.encode("latin-1", "ignore").decode("latin-1")
        pdf.cell(200, 8, txt=clean, ln=True)
    out_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(out_path)
    return out_path

if master_file and compare_files:
    st.success("Files uploaded successfully.")
    df_master = pd.read_excel(master_file, header=None)
    header_info = extract_invoice_data(df_master)
    product_info = extract_product_rows(df_master)
    doc_texts = {doc.name: extract_text(doc) for doc in compare_files}

    header_results = match_fields_against_docs(header_info, doc_texts)
    product_results = match_products_against_docs(product_info, doc_texts)

    df1 = pd.DataFrame(header_results)
    df2 = pd.DataFrame(product_results)

    st.header("🔍 Header Field Check")
    st.dataframe(df1, use_container_width=True)

    st.header("📦 Product-Level Check")
    st.dataframe(df2, use_container_width=True)

    csv = pd.concat([df1, df2], axis=0).to_csv(index=False).encode()
    st.download_button("📥 Download CSV Report", csv, file_name="v9c_comparison_report.csv", mime="text/csv")

    pdf_path = export_pdf(pd.concat([df1, df2], axis=0))
    with open(pdf_path, "rb") as f:
        st.download_button("🖨️ Download PDF Report", f, file_name="v9c_comparison_report.pdf", mime="application/pdf")
else:
    st.info("Please upload your Invoice/Packing List Excel and comparison documents.")
