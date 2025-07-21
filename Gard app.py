import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Initialize session state variables
if 'scanned_barcodes' not in st.session_state:
    st.session_state.scanned_barcodes = []
if 'last_scanned' not in st.session_state:
    st.session_state.last_scanned = ""
if 'barcode_temp' not in st.session_state:
    st.session_state.barcode_temp = ""

# File uploader
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names)
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()

    required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ Sheet must contain these columns: {required_columns}")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    # تنظيف الأعمدة
    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)

    # Barcode input and control buttons
    st.markdown("### 📸 Scan Barcode")
    barcode_col, button_col, clear_col = st.columns([4, 1, 1])

    with barcode_col:
        input_val = st.text_input("Scan Barcode", value=st.session_state.barcode_temp, key="barcode_field")

    with button_col:
        confirm_pressed = st.button("✔️ Confirm")

    with clear_col:
        clear_pressed = st.button("🧹 Clear")

    product_name_display = ""

    if confirm_pressed:
        scanned = input_val.strip()
        if scanned:
            st.session_state.scanned_barcodes.append(scanned)
            st.session_state.last_scanned = scanned

            if scanned in df["Barcodes"].values:
                df.loc[df["Barcodes"] == scanned, "Actual Quantity"] += 1
                product_name_display = df.loc[df["Barcodes"] == scanned, "Product Name"].values[0]
            else:
                product_name_display = "❌ Not Found"

            # Clear input manually
            st.session_state.barcode_temp = ""

    elif clear_pressed:
        st.session_state.barcode_temp = ""
        st.session_state.last_scanned = ""
        product_name_display = ""

    else:
        if st.session_state.last_scanned:
            scanned = st.session_state.last_scanned
            if scanned in df["Barcodes"].values:
                product_name_display = df.loc[df["Barcodes"] == sca]()
