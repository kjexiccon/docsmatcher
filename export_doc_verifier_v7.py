
import streamlit as st
import pandas as pd
import fitz
import docx
import tempfile

st.set_page_config(page_title="SHEESH SPICES Verifier – v7", layout="wide")
st.markdown("## 📦 SHEESH SPICES Export Document Verifier – v7")
st.markdown("Improved layout, cross-document comparison, and strict validation alerts.")

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
        return text.lower()
    else:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs]).lower()

def parse_master_products(df):
    product_data = []
    for _, row in df.iterrows():
        product = row.get("Product", "").strip().upper()
        hs = row.get("HS Code", "").strip()
        qty = str(row.get("Quantity", "")).strip()
        product_data.append({
            "Product": product,
            "HS Code": hs,
            "Quantity": qty
        })
    return product_data

def compare_across_docs(product_data, doc_texts):
    results = []
    for prod in product_data:
        status_summary = []
        for docname, text in doc_texts.items():
            name_match = prod["Product"] in text
            hs_match = prod["HS Code"] in text
            qty_match = prod["Quantity"] in text

            reasons = []
            if not name_match:
                reasons.append(f"❌ Product mismatch in {docname}: expected '{prod['Product']}'")
            if not hs_match:
                reasons.append(f"❌ HS code mismatch in {docname}")
            if not qty_match:
                reasons.append(f"❌ Quantity mismatch in {docname}")
            if not reasons:
                status_summary.append(f"✅ {docname}")
            else:
                status_summary.extend(reasons)

        if all("✅" in s for s in status_summary):
            alert = f"✅ All documents match for {prod['Product']}"
        else:
            alert = f"🔎 Issues for {prod['Product']}\n" + "\n".join([s for s in status_summary if "❌" in s])

        results.append({
            "Product": prod["Product"],
            "HS Code": prod["HS Code"],
            "Quantity": prod["Quantity"],
            "Alert": alert
        })
    return results

if master_file and compare_files:
    st.success("Files uploaded successfully.")
    df_master = pd.read_excel(master_file).fillna("").astype(str)
    product_data = parse_master_products(df_master)

    doc_texts = {doc.name: extract_text(doc) for doc in compare_files}
    comparison = compare_across_docs(product_data, doc_texts)

    for entry in comparison:
        st.markdown(f"### 🧾 {entry['Product']}")
        st.markdown(f"- **HS Code**: {entry['HS Code']}")
        st.markdown(f"- **Quantity**: {entry['Quantity']}")
        if entry["Alert"].startswith("✅"):
            st.success(entry["Alert"])
        else:
            st.error(entry["Alert"])
        st.markdown("---")
else:
    st.info("Upload a master Excel file and at least one document to begin verification.")
