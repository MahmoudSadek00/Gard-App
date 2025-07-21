import streamlit as st
import pandas as pd
from io import StringIO
import datetime

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📷 Inventory Scanner with Camera")

# Step 1: Upload products sheet
uploaded_file = st.file_uploader("Upload Product Sheet (CSV or Excel)", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Ensure columns exist
    if not {"Barcodes", "Available Quantity"}.issubset(df.columns):
        st.error("Sheet must include 'Barcodes' and 'Available Quantity'.")
        st.stop()

    # Force Barcodes to string for safe merging
    df["Barcodes"] = df["Barcodes"].astype(str)

    # Session state for scan counts
    if "scan_data" not in st.session_state:
        st.session_state.scan_data = {}

    # === Barcode scanner via camera ===
    st.subheader("📸 Scan Barcode")
    barcode = st.text_input("Scanned barcode will appear here", key="barcode_input")

    # Embed HTML5 camera barcode scanner
    st.components.v1.html(
        """
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
        <div id="reader" style="width: 300px;"></div>
        <script>
        function domReady(fn) {
            if (document.readyState === "interactive" || document.readyState === "complete") {
                fn();
            } else {
                document.addEventListener("DOMContentLoaded", fn);
            }
        }

        domReady(function () {
            let lastResult = "";
            const html5QrCode = new Html5Qrcode("reader");
            const config = { fps: 10, qrbox: 250 };

            html5QrCode.start(
                { facingMode: "environment" },
                config,
                (decodedText, decodedResult) => {
                    if (decodedText !== lastResult) {
                        lastResult = decodedText;
                        const input = window.parent.document.querySelector('input[id="barcode_input"]');
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        nativeInputValueSetter.call(input, decodedText);
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }
            );
        });
        </script>
        """,
        height=320,
    )

    # Count scan
    if barcode:
        barcode = barcode.strip()
        st.session_state.scan_data[barcode] = st.session_state.scan_data.get(barcode, 0) + 1
        st.success(f"Scanned: {barcode} | Total: {st.session_state.scan_data[barcode]}")

    # Create scanned dataframe
    scanned_df = pd.DataFrame([
        {"Barcodes": code, "Actual Quantity": qty}
        for code, qty in st.session_state.scan_data.items()
    ])
    scanned_df["Barcodes"] = scanned_df["Barcodes"].astype(str)

    # Merge & calculate difference
    merged = pd.merge(df, scanned_df, on="Barcodes", how="left")
    merged["Actual Quantity"] = merged["Actual Quantity"].fillna(0).astype(int)
    merged["Difference"] = merged["Actual Quantity"] - merged["Available Quantity"]

    st.subheader("📊 Scanned Data")
    st.dataframe(merged, use_container_width=True)

    # Download
    csv = merged.to_csv(index=False).encode('utf-8')
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    st.download_button("📥 Download CSV", data=csv, file_name=f"inventory_scan_{now}.csv", mime='text/csv')

    # Reset
    if st.button("🔁 Reset Scans"):
        st.session_state.scan_data = {}
        st.success("Scan data cleared.")
