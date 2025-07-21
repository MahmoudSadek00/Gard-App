import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📷 Barcode Scanner - Inventory App")

# Upload initial inventory file
uploaded_file = st.file_uploader("Upload Inventory File (Excel)", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
        st.error("File must contain 'Barcodes' and 'Available Quantity' columns.")
        st.stop()

    if "Actual Quantity" not in df.columns:
        df["Actual Quantity"] = 0
    if "Difference" not in df.columns:
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    st.subheader("📦 Inventory Table")
    table_placeholder = st.empty()

    # JavaScript barcode scanner
    st.markdown("### Scan a barcode")
    html(
        """
        <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
        <div id="reader" style="width:300px"></div>
        <script>
            const qrcode = new Html5Qrcode("reader");
            const config = { fps: 10, qrbox: 250 };
            qrcode.start(
                { facingMode: "environment" },
                config,
                (decodedText, decodedResult) => {
                    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                    if (input) {
                        input.value = decodedText;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                },
                errorMessage => {}
            ).catch(err => {});
        </script>
        """,
        height=400,
    )

    barcode = st.text_input("Scanned Barcode")

    if barcode:
        # تحديث الكمية الفعلية
        if barcode in df["Barcodes"].values:
            df.loc[df["Barcodes"] == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
        else:
            st.warning(f"Barcode {barcode} not found in file.")

        table_placeholder.dataframe(df)

        # زر تحميل النتيجة
        output_file = "inventory_with_actual.xlsx"
        df.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("📥 Download Updated File", f, file_name="Inventory_Updated.xlsx")

