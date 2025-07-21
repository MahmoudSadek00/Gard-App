import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Session state init
if 'barcode_counts' not in st.session_state:
    st.session_state.barcode_counts = {}
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ""
if 'df' not in st.session_state:
    st.session_state.df = None

# File uploader
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file and st.session_state.df is None:
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

    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)
    st.session_state.df = df.copy()

if st.session_state.df is not None:
    df = st.session_state.df

    st.markdown("### 📸 Scan Barcode")
    col1, col2 = st.columns([4, 1])

    # إدخال الباركود
    with col1:
        scanned = st.text_input("Scan Barcode", value=st.session_state.barcode_input, key="barcode_input")

    # أزرار
    with col2:
        if st.button("✅ Confirm"):
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

        if st.button("❌ Clear"):
            st.session_state.barcode_input = ""

    # اسم المنتج
    product_name_display = ""
    if scanned and scanned in df["Barcodes"].values:
        product_name_display = df.loc[df["Barcodes"] == scanned, "Product Name"].values[0]
    elif scanned:
        product_name_display = "❌ Not Found"

    st.markdown("#### 🏷️ Product Name")
    st.markdown(f"""
        <div style="padding: 0.75rem 1rem; background-color: #e6f4ea; border: 2px solid #2e7d32;
                    border-radius: 5px; font-weight: bold; font-size: 16px;">
            {product_name_display}
        </div>
    """, unsafe_allow_html=True)

    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    st.subheader("📋 Updated Sheet")
    st.dataframe(df)

    st.markdown("### ✅ Scanned Barcode Log")
    st.write(pd.DataFrame([
        {"Barcode": k, "Scanned Count": v}
        for k, v in st.session_state.barcode_counts.items()
    ]))

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(df)
    st.download_button("📥 Download Updated Sheet", data=csv, file_name="updated_inventory.csv", mime="text/csv")
