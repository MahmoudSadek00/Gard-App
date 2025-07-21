import streamlit as st
import pandas as pd
from io import StringIO
import datetime

st.set_page_config(page_title="📦 Inventory Scanning App", layout="wide")
st.title("📦 Inventory Scanning App with Barcode Scanner")

# Step 1: Upload products sheet
uploaded_file = st.file_uploader("Upload Product Sheet (CSV or Excel)", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Ensure it has Barcodes and Available Quantity
    if not {"Barcodes", "Available Quantity"}.issubset(df.columns):
        st.error("Product sheet must have 'Barcodes' and 'Available Quantity' columns.")
        st.stop()

    # Initialize session state
    if "scan_data" not in st.session_state:
        st.session_state.scan_data = {}

    # Step 2: Barcode input manually (camera will be added below)
    st.subheader("Scan Barcode (type or scan):")
    barcode = st.text_input("Scan or type barcode:", key="barcode_input")

    if barcode:
        st.session_state.scan_data[barcode] = st.session_state.scan_data.get(barcode, 0) + 1
        st.success(f"Scanned: {barcode} | Total: {st.session_state.scan_data[barcode]}")

    # Step 3: Display scanned data
    st.subheader("Scanned Results:")
    scanned_df = pd.DataFrame([
        {"Barcodes": code, "Actual Quantity": qty}
        for code, qty in st.session_state.scan_data.items()
    ])

    # Merge with original data
    merged = pd.merge(df, scanned_df, on="Barcodes", how="left")
    merged["Actual Quantity"] = merged["Actual Quantity"].fillna(0).astype(int)
    merged["Difference"] = merged["Actual Quantity"] - merged["Available Quantity"]

    st.dataframe(merged, use_container_width=True)

    # Step 4: Export
    csv = merged.to_csv(index=False).encode('utf-8')
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    st.download_button("📥 Download CSV", data=csv, file_name=f"inventory_scan_{now}.csv", mime='text/csv')

    # Step 5: Clear scans
    if st.button("🗑️ Reset Scans"):
        st.session_state.scan_data = {}
        st.success("Scan data cleared.")
