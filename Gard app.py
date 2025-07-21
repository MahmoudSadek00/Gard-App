import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner")

# -------------------- Session State Initialization -------------------- #
if "excel_file" not in st.session_state:
    st.session_state.excel_file = None
if "sheet_names" not in st.session_state:
    st.session_state.sheet_names = []
if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
if "barcode_input" not in st.session_state:
    st.session_state.barcode_input = ""

# -------------------- File Upload -------------------- #
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])
if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    st.session_state.excel_file = xls
    st.session_state.sheet_names = xls.sheet_names
    st.session_state.selected_sheet = None
    st.session_state.df = pd.DataFrame()

# -------------------- Sheet Selection -------------------- #
if st.session_state.excel_file:
    selected = st.selectbox("Select Brand Sheet", st.session_state.sheet_names)
    if selected != st.session_state.selected_sheet:
        df = st.session_state.excel_file.parse(selected)

        # Ensure required columns
        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("Sheet must contain 'Barcodes' and 'Available Quantity' columns.")
            st.stop()

        if "Actual Quantity" not in df.columns:
            df["Actual Quantity"] = 0
        if "Product Name" not in df.columns:
            df["Product Name"] = ""

        st.session_state.df = df
        st.session_state.selected_sheet = selected

# -------------------- Barcode Logic -------------------- #
def handle_barcode():
    barcode = st.session_state.barcode_input.strip()
    df = st.session_state.df.copy()
    match = df["Barcodes"] == barcode

    if match.any():
        df.loc[match, "Actual Quantity"] += 1
        st.session_state.df = df
        st.success(f"✅ Counted: {barcode}")
    else:
        st.warning("⚠️ Barcode not found.")

    st.session_state.barcode_input = ""  # Reset safely within the callback

# -------------------- Barcode Input Field -------------------- #
if not st.session_state.df.empty:
    st.subheader("🔍 Scan or Enter Barcode")
    st.text_input(
        "Enter or Scan Barcode",
        key="barcode_input",
        on_change=handle_barcode
    )

# -------------------- DataFrame Preview -------------------- #
if not st.session_state.df.empty:
    st.dataframe(st.session_state.df, use_container_width=True)
