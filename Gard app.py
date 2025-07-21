import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")

st.title("📦 Inventory Scanner")

# Initialize session state variables
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

if "sheet_name" not in st.session_state:
    st.session_state.sheet_name = None

# Step 1: Upload file
if not st.session_state.file_uploaded:
    uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])
    if uploaded_file is not None:
        xls = pd.ExcelFile(uploaded_file)
        st.session_state.sheet_names = xls.sheet_names
        st.session_state.excel_file = xls
        st.session_state.file_uploaded = True
        st.experimental_rerun()

# Step 2: Select sheet
if st.session_state.file_uploaded and not st.session_state.df.shape[0]:
    sheet = st.selectbox("Select Brand Sheet", st.session_state.sheet_names)
    df = st.session_state.excel_file.parse(sheet)
    
    # Ensure required columns exist
    expected_cols = ['Barcodes', 'Available Quantity']
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"Missing column: {col}")
            st.stop()
    
    # Add Product Name if needed
    if 'Product Name' not in df.columns:
        df['Product Name'] = ""
    
    # Add Actual Quantity column if not exists
    if 'Actual Quantity' not in df.columns:
        df['Actual Quantity'] = 0

    st.session_state.df = df
    st.session_state.sheet_name = sheet

# Step 3: Show barcode scanner input
if st.session_state.df.shape[0]:
    st.subheader(f"Scanning Sheet: {st.session_state.sheet_name}")

    barcode = st.text_input("🔍 Scan or Enter Barcode", key="barcode_input")

    if barcode:
        df = st.session_state.df.copy()
        matched = df['Barcodes'] == barcode

        if matched.any():
            df.loc[matched, 'Actual Quantity'] += 1
            st.success(f"✅ Barcode '{barcode}' updated.")
        else:
            st.warning("⚠️ Barcode not found.")

        st.session_state.df = df
        st.session_state.barcode_input = ""  # Clear input
        st.experimental_rerun()

    st.dataframe(st.session_state.df, use_container_width=True)
