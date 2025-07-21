import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Initial session state setup
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'sheet_names' not in st.session_state:
    st.session_state.sheet_names = []
if 'selected_sheet' not in st.session_state:
    st.session_state.selected_sheet = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ""

# Uploading the file (only if not already uploaded)
if st.session_state.uploaded_file is None:
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"], key="file_uploader")
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
        st.session_state.sheet_names = list(all_sheets.keys())
        st.session_state.all_sheets_data = all_sheets

# Selecting sheet
if st.session_state.uploaded_file and st.session_state.sheet_names:
    selected = st.selectbox("Select Sheet", st.session_state.sheet_names)
    if selected != st.session_state.selected_sheet:
        st.session_state.selected_sheet = selected
        df = st.session_state.all_sheets_data[selected]
        df.columns = df.columns.str.strip()

        # Check required columns
        required_cols = ["Barcodes", "Available Quantity", "Product Name"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"❌ Missing required column: {col}")
                st.stop()

        # Prepare DataFrame
        df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
        df["Actual Quantity"] = 0  # Initialize if not present
        st.session_state.df = df.copy()

# Barcode Scanning Interface
if st.session_state.df is not None:
    df = st.session_state.df

    st.markdown("### 📸 Scan a Barcode")
    barcode = st.text_input("Scan Barcode", key="barcode_input", value="", label_visibility="collapsed")

    product_name_display = ""
    if barcode:
        barcode = barcode.strip()
        if barcode in df["Barcodes"].values:
            current_qty = df.loc[df["Barcodes"] == barcode, "Actual Quantity"].values[0]
            df.loc[df["Barcodes"] == barcode, "Actual Quantity"] = current_qty + 1
            product_name_display = df.loc[df["Barcodes"] == barcode, "Product Name"].values[0]
        else:
            product_name_display = "❌ Not Found"

        st.session_state.df = df
        st.session_state.barcode_input = ""  # Clear input

        # Rerun to reset text_input
        st.experimental_rerun()

    # Display result
    if product_name_display:
        st.markdown("#### 🏷️ Product Name")
        st.markdown(f"""
            <div style="padding: 10px; background-color: #e6f4ea; border: 2px solid #2e7d32;
                        border-radius: 5px; font-weight: bold; font-size: 16px;">
                {product_name_display}
            </div>
        """, unsafe_allow_html=True)

    # Show updated table
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
    st.markdown("### 📋 Updated Table")
    st.dataframe(df)

    # Scanned Log
    st.markdown("### ✅ Scanned Barcodes")
    scanned_df = df[df["Actual Quantity"] > 0][["Barcodes", "Actual Quantity"]]
    st.dataframe(scanned_df)

    # Download option
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df(df)
    st.download_button("📥 Download Updated Sheet", csv, "updated_inventory.csv", "text/csv")
