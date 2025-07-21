import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory Scanner")

# Session state initialization
if "df" not in st.session_state:
    st.session_state.df = None
if "barcode_counts" not in st.session_state:
    st.session_state.barcode_counts = {}
if "barcode_input" not in st.session_state:
    st.session_state.barcode_input = ""
if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None

# File uploader
uploaded_file = st.file_uploader("📤 Upload Inventory Excel File", type=["xlsx"])

# Sheet selector
if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    st.session_state.selected_sheet = st.selectbox("📂 Select Brand Sheet", sheet_names)

    if st.session_state.selected_sheet:
        df = all_sheets[st.session_state.selected_sheet]
        df.columns = df.columns.str.strip()

        required_cols = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ Sheet must include columns: {required_cols}")
            st.stop()

        # Clean and prepare
        df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
        df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)
        df["Available Quantity"] = df["Available Quantity"].fillna(0).astype(int)

        st.session_state.df = df.copy()

# Main app
if st.session_state.df is not None:
    df = st.session_state.df
    st.markdown("### 📸 Scan or Enter Barcode")
    scanned = st.text_input("Scan Barcode", key="barcode_input")

    product_name_display = ""

    if scanned:
        scanned = scanned.strip()

        # Update barcode count
        count = st.session_state.barcode_counts.get(scanned, 0) + 1
        st.session_state.barcode_counts[scanned] = count

        if scanned in df["Barcodes"].values:
            df.loc[df["Barcodes"] == scanned, "Actual Quantity"] = count
            product_name_display = df.loc[df["Barcodes"] == scanned, "Product Name"].values[0]
        else:
            product_name_display = "❌ Not Found"

        # Save update
        st.session_state.df = df

        # Clear input on rerun
        st.session_state.barcode_input = ""
        st.experimental_rerun()

    # Show product name
    st.markdown("#### 🏷️ Product Name")
    st.markdown(f"""
        <div style="padding: 0.75rem 1rem; background-color: #e3f2fd; border: 2px solid #2196f3;
                    border-radius: 5px; font-weight: bold; font-size: 16px;">
            {product_name_display}
        </div>
    """, unsafe_allow_html=True)

    # Calculate difference
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    st.subheader("📋 Inventory Table")
    st.dataframe(df)

    # Scanned log
    st.markdown("### ✅ Scanned Barcode Log")
    st.dataframe(pd.DataFrame([
        {"Barcode": k, "Scanned Count": v}
        for k, v in st.session_state.barcode_counts.items()
    ]))

    # Download updated sheet
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    st.download_button("📥 Download Updated Inventory", data=convert_df_to_csv(df),
                       file_name="updated_inventory.csv", mime="text/csv")
