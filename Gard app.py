import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")

st.title("📦 Inventory Scanner")

# Step 1: Initialize session state variables
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "excel_file" not in st.session_state:
    st.session_state.excel_file = None
if "sheet_names" not in st.session_state:
    st.session_state.sheet_names = []
if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Step 2: Upload file
if not st.session_state.file_uploaded:
    uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])
    if uploaded_file is not None:
        xls = pd.ExcelFile(uploaded_file)
        st.session_state.excel_file = xls
        st.session_state.sheet_names = xls.sheet_names
        st.session_state.file_uploaded = True
        st.experimental_rerun()

# Step 3: Sheet selector
if st.session_state.file_uploaded:
    st.subheader("🧾 Select Brand Sheet")
    selected_sheet = st.selectbox("Choose a sheet", st.session_state.sheet_names, key="sheet_selector")

    if st.session_state.selected_sheet != selected_sheet:
        st.session_state.selected_sheet = selected_sheet
        # Load sheet data
        df = st.session_state.excel_file.parse(selected_sheet)

        # Add necessary columns if not found
        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("Sheet must contain 'Barcodes' and 'Available Quantity' columns.")
            st.stop()

        if "Actual Quantity" not in df.columns:
            df["Actual Quantity"] = 0

        if "Product Name" not in df.columns:
            df["Product Name"] = ""

        st.session_state.df = df

# Step 4: Barcode scanner logic
if not st.session_state.df.empty:
    st.subheader("🔍 Scan Barcode")

    barcode = st.text_input("Scan or Enter Barcode", key="barcode_input")

    if barcode:
        df = st.session_state.df.copy()
        matches = df["Barcodes"] == barcode

        if matches.any():
            df.loc[matches, "Actual Quantity"] += 1
            st.success(f"✅ Barcode '{barcode}' found and updated.")
        else:
            st.warning("⚠️ Barcode not found.")

        st.session_state.df = df
        st.experimental_rerun()

    # Display updated table
    st.dataframe(st.session_state.df, use_container_width=True)

