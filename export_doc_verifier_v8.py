
import streamlit as st
import pandas as pd
import fitz
import docx
import tempfile

st.set_page_config(page_title="SHEESH SPICES Verifier – v8", layout="wide")
st.title("📦 SHEESH SPICES Export Document Verifier – v8")
st.markdown("Improved UI, strict string matching (no fuzzy logic), and cross-document smart alerts.")

st.markdown("---")

st.sidebar.header("📂 Upload Files")
master_file = st.sidebar.file_uploader("Primary Invoice or Packing List (Excel)", type=["xlsx"])
compare_files = st.sidebar.file_uploader("Compare Docs (COO, Phyto, Fumi, B/L)", type=["pdf", "docx"], accept_multiple_files=True)

def extract_text(file):
    if file.name.endswith(".pdf"):
        text = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            tmp.flush()
            doc = fitz.open(tmp.name)
            for page in doc:
                text += page.get_text()
        return text.upper()
    else:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs]).upper()

def parse_master_products(df):
    product_data = []
    for _, row in df.iterrows():
        product = row.get("Product", "").strip().upper()
        hs = row.get("HS Code", "").strip()
        qty = str(row.get("Quantity", "")).strip()
        if product:  # Only include rows with products
            product_data.append({
                "Product": product,
                "HS Code": hs,
                "Quantity": qty
            })
    return product_data

def compare_fields_strict(prod, doc_text, docname):
    messages = []
    if prod["Product"] not in doc_text:
        messages.append(f"❌ Product name mismatch in {docname}: found '{prod['Product']}'")
    if prod["HS Code"] and prod["HS Code"] not in doc_text:
        messages.append(f"❌ HS code mismatch in {docname}")
    if prod["Quantity"] and prod["Quantity"] not in doc_text:
        messages.append(f"❌ Quantity mismatch in {docname}")
    return messages

def cross_doc_comparison(master_rows, doc_texts):
    results = []
    for prod in master_rows:
        product_alerts = []
        match_count = 0
        for docname, doc_text in doc_texts.items():
            issues = compare_fields_strict(prod, doc_text, docname)
            if not issues:
                product_alerts.append(f"✅ {docname}")
                match_count += 1
            else:
                product_alerts.extend(issues)

        if match_count == len(doc_texts):
            alert = f"✅ All documents match for {prod['Product']}"
        else:
            alert = f"🔎 Issues for {prod['Product']}\n" + "\n".join([a for a in product_alerts if '❌' in a])
        results.append({
            "Product": prod["Product"],
            "HS Code": prod["HS Code"],
            "Quantity": prod["Quantity"],
            "Alerts": product_alerts,
            "Summary": alert
        })
    return results

if master_file and compare_files:
    st.success("✅ Files uploaded successfully.")
    df_master = pd.read_excel(master_file).fillna("").astype(str)
    master_rows = parse_master_products(df_master)

    doc_texts = {doc.name: extract_text(doc) for doc in compare_files}
    summary = cross_doc_comparison(master_rows, doc_texts)

    for entry in summary:
        with st.expander(f"📦 {entry['Product']}"):
            st.markdown(f"- **HS Code:** {entry['HS Code']}")
            st.markdown(f"- **Quantity:** {entry['Quantity']}")
            for msg in entry["Alerts"]:
                if msg.startswith("✅"):
                    st.success(msg)
                else:
                    st.error(msg)
            st.markdown("---")
else:
    st.info("Upload a master Excel file and at least one document to begin verification.")
