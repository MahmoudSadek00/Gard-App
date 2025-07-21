import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd
from streamlit.components.v1 import html

st.set_page_config(layout="wide")
st.title("📸 Barcode Scanner Test")

# Upload Excel File
uploaded_file = st.file_uploader("Upload Excel with Barcodes", type=["xlsx"])
if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names)
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()

    if "Barcodes" not in df.columns:
        st.error("Sheet must contain a 'Barcodes' column.")
        st.stop()

    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    if "Actual Quantity" not in df.columns:
        df["Actual Quantity"] = 0

    st.session_state.df = df

# JS + HTML camera barcode scanner
st.markdown("### 📷 Scan Barcode Below")
html("""
<script src="https://unpkg.com/html5-qrcode@2.3.7/html5-qrcode.min.js"></script>
<div id="reader" style="width: 300px;"></div>
<input type="text" id="hiddenInput" style="display:none"/>
<script>
  function onScanSuccess(decodedText, decodedResult) {
      document.getElementById("hiddenInput").value = decodedText;
      const event = new Event("input", { bubbles: true });
      document.getElementById("hiddenInput").dispatchEvent(event);
  }

  if (!window.qrStarted) {
      const html5QrCode = new Html5Qrcode("reader");
      html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: 250 }, onScanSuccess);
      window.qrStarted = true;
  }
</script>
""", height=300)

# Read barcode value from hidden input
barcode = streamlit_js_eval(js_expressions="document.getElementById('hiddenInput').value", key="barcode_eval")

if barcode:
    barcode = barcode.strip()
    st.success(f"✅ Barcode Scanned: {barcode}")

    if barcode in st.session_state.df["Barcodes"].values:
        st.session_state.df.loc[st.session_state.df["Barcodes"] == barcode, "Actual Quantity"] += 1
        st.success("✅ Quantity updated!")
    else:
        st.error("❌ Barcode not found in sheet.")

    st.dataframe(st.session_state.df)

    csv = st.session_state.df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="updated_inventory.csv", mime="text/csv")
