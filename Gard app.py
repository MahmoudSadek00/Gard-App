import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner")

# ---------- SESSION STATE INIT ----------
if "step" not in st.session_state:
    st.session_state.step = "upload"
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

# ---------- STEP 1: UPLOAD FILE ----------
if st.session_state.step == "upload":
    uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])
    if uploaded_file:
        xls = pd.ExcelFile(uploaded_file)
        st.session_state.excel_file = xls
        st.session_state.sheet_names = xls.sheet_names
        st.session_state.step = "select_sheet"
        st.experimental_rerun()

# ---------- STEP 2: SELECT SHEET ----------
elif st.session_state.step == "select_sheet":
    st.subheader("🧾 Select Brand Sheet")
    selected_sheet = st.selectbox(
        "Select sheet", st.session_state.sheet_names, key="sheet_selector"
    )

    if selected_sheet != st.session_state.selected_sheet:
        df = st.session_state.excel_file.parse(selected_sheet)

        # Ensure required columns exist
        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("❌ Sheet must contain 'Barcodes' and 'Available Quantity' columns.")
            st.stop()

        if "Actual Quantity" not in df.columns:
            df["Actual Quantity"] = 0

        if "Product Name" not in df.columns:
            df["Product Name"] = ""

        st.session_state.df = df
        st.session_state.selected_sheet = selected_sheet
    st.session_state.step = "scan"
    st.experimental_rerun()

# ---------- STEP 3: SCAN BARCODE ----------
elif st.session_state.step == "scan":
    st.subheader(f"✅ Brand: {st.session_state.selected_sheet}")
    df = st.session_state.df.copy()

    st.divider()
    st.subheader("🔍 Scan or Enter Barcode")
    barcode_input = st.text_input("Enter or Scan Barcode", value="", key="barcode_input")

    if barcode_input:
        matches = df["Barcodes"] == barcode_input
        if matches.any():
            df.loc[matches, "Actual Quantity"] += 1
            st.success(f"✅ Barcode '{barcode_input}' counted.")
        else:
            st.warning("⚠️ Barcode not found in sheet.")

        # Update session
        st.session_state.df = df

        # Rerun to clear input
        st.experimental_rerun()

    st.subheader("📊 Inventory Table")
    st.dataframe(df, use_container_width=True)
