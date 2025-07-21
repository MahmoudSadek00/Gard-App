import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Session state setup
if 'barcode_counts' not in st.session_state:
    st.session_state.barcode_counts = {}
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ""
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'sheet_names' not in st.session_state:
    st.session_state.sheet_names = []
if 'selected_sheet' not in st.session_state:
    st.session_state.selected_sheet = None
if 'df' not in st.session_state:
    st.session_state.df = None

# Step 1: File upload (دائمًا ظاهر)
st.markdown("### 📤 Upload Inventory File")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"], key="file_uploader")

if uploaded_file:
    if uploaded_file != st.session_state.uploaded_file:
        all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
        st.session_state.uploaded_file = uploaded_file
        st.session_state.sheet_names = list(all_sheets.keys())
        st.session_state.selected_sheet = None
        st.session_state.df = None

# Step 2: Show dropdown if sheets available
if st.session_state.uploaded_file and st.session_state.sheet_names:
    st.session_state.selected_sheet = st.selectbox("Select Brand Sheet", st.session_state.sheet_names)

    # Step 3: Load selected sheet
    if st.session_state.selected_sheet:
        all_sheets = pd.read_excel(st.session_state.uploaded_file, sheet_name=None)
        df = all_sheets[st.session_state.selected_sheet]
        df.columns = df.columns.str.strip()

        required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
        if not all(col in df.columns for col in required_columns):
            st.error(f"❌ Sheet must contain: {required_columns}")
            st.stop()

        df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
        df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)
        st.session_state.df = df.copy()

# Step 4: Scanning page
if st.session_state.df is not None:
    df = st.session_state.df

    st.markdown("### 📸 Scan Barcode")
    scanned = st.text_input("Scan Barcode", value=st.session_state.barcode_input)
    product_name_display = ""

    if scanned:
        scanned = scanned.strip()
        if scanned in st.session_state.barcode_counts:
            st.session_state.barcode_counts[scanned] += 1
        else:
            st.session_state.barcode_counts[scanned] = 1

        if scanned in df["Barcodes"].values:
            count = st.session_state.barcode_counts[scanned]
            df.loc[df["Barcodes"] == scanned, "Actual Quantity"] = count
            product_name_display = df.loc[df["Barcodes"] == scanned, "Product Name"].values[0]
        else:
            product_name_display = "❌ Not Found"

        st.session_state.df = df
        st.session_state.barcode_input = ""
    else:
        st.session_state.barcode_input = scanned

    # Display product name
    st.markdown("#### 🏷️ Product Name")
    st.markdown(f"""
        <div style="padding: 0.75rem 1rem; background-color: #e6f4ea; border: 2px solid #2e7d32;
                    border-radius: 5px; font-weight: bold; font-size: 16px;">
            {product_name_display}
        </div>
    """, unsafe_allow_html=True)

    # Show updated sheet
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
    st.subheader("📋 Updated Sheet")
    st.dataframe(df)

    # Barcode log
    st.markdown("### ✅ Scanned Barcode Log")
    st.write(pd.DataFrame([
        {"Barcode": k, "Scanned Count": v}
        for k, v in st.session_state.barcode_counts.items()
    ]))

    # Download CSV
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(df)
    st.download_button("📥 Download Updated Sheet", data=csv, file_name="updated_inventory.csv", mime="text/csv")
