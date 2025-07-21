import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")

st.title("📦 Inventory Scanner")

# Initial session state
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "excel_file" not in st.session_state:
    st.session_state.excel_file = None
if "sheet_names" not in st.session_state:
    st.session_state.sheet_names = []
if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "barcode" not in st.session_state:
    st.session_state.barcode = ""

# Uploading the file
if not st.session_state.uploaded:
    uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])
    if uploaded_file:
        xls = pd.ExcelFile(uploaded_file)
        st.session_state.excel_file = xls
        st.session_state.sheet_names = xls.sheet_names
        st.session_state.uploaded = True
        st.experimental_rerun()

# After file uploaded
if st.session_state.uploaded:
    st.subheader("🧾 Select Sheet (Brand)")
    selected_sheet = st.selectbox(
        "Select a sheet to inventory", st.session_state.sheet_names, key="sheet_selector"
    )

    # If sheet changed, load data
    if selected_sheet != st.session_state.selected_sheet:
        df = st.session_state.excel_file.parse(selected_sheet)

        # Ensure required columns
        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("❌ Sheet must contain 'Barcodes' and 'Available Quantity' columns.")
            st.stop()

        if "Actual Quantity" not in df.columns:
            df["Actual Quantity"] = 0

        if "Product Name" not in df.columns:
            df["Product Name"] = ""

        st.session_state.df = df
        st.session_state.selected_sheet = selected_sheet

    # Show barcode input and table
    df = st.session_state.df.copy()

    st.divider()
    st.subheader("🔍 Scan Barcode")
    barcode_input = st.text_input("Enter or Scan Barcode", value=st.session_state.barcode, key="barcode_input")

    if barcode_input:
        matches = df["Barcodes"] == barcode_input
        if matches.any():
            df.loc[matches, "Actual Quantity"] += 1
            st.success(f"✅ Barcode '{barcode_input}' found and counted.")
        else:
            st.warning("⚠️ Barcode not found.")

        # Update session
        st.session_state.df = df
        st.session_state.barcode = ""  # Clear input
        st.experimental_rerun()  # Refresh to clear input

    # Show dataframe
    st.subheader("📊 Inventory Table")
    st.dataframe(st.session_state.df, use_container_width=True)
