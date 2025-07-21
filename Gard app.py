import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Session state setup
if 'scanned_barcodes' not in st.session_state:
    st.session_state.scanned_barcodes = []

# File upload
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())

    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names)
    df = all_sheets[selected_sheet]
    df = df.rename(columns=lambda x: x.strip())

    if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
        st.error("The sheet must contain 'Barcodes' and 'Available Quantity' columns.")
        st.stop()

    # Barcode input comes first (before table)
    st.markdown("### 📸 Scan Barcode")
    barcode_input = st.text_input("Scan Here", value="", label_visibility="collapsed")

    if barcode_input:
        st.session_state.scanned_barcodes.append(barcode_input)
        # Clear input manually by forcing empty
        st.text_input("Last Scanned", value=barcode_input, disabled=True)
        barcode_input = ""  # Reset local var

    # Process scanned barcodes
    scanned_df = pd.DataFrame(st.session_state.scanned_barcodes, columns=["Barcodes"])
    scanned_df["Actual Quantity"] = 1
    scanned_df = scanned_df.groupby("Barcodes").sum().reset_index()

    # Merge scanned data with original sheet
    merged = pd.merge(df, scanned_df, on="Barcodes", how="left")
    merged["Actual Quantity"] = merged["Actual Quantity"].fillna(0).astype(int)
    merged["Difference"] = merged["Actual Quantity"] - merged["Available Quantity"]

    # Show original sheet and live updates
    st.subheader("📋 Updated Inventory Sheet")
    st.dataframe(merged)

    # Download CSV
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(merged)
    st.download_button("📥 Download Updated Inventory (CSV)", data=csv, file_name="updated_inventory.csv", mime="text/csv")
