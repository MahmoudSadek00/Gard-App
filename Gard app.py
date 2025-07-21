import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Session state setup
if 'barcode_counts' not in st.session_state:
    st.session_state.barcode_counts = {}
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ""
if 'df' not in st.session_state:
    st.session_state.df = None
if 'selected_sheet' not in st.session_state:
    st.session_state.selected_sheet = None
if 'product_name_display' not in st.session_state:
    st.session_state.product_name_display = ""

# File uploader
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())

    if st.session_state.selected_sheet not in sheet_names:
        st.session_state.selected_sheet = sheet_names[0]

    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names, index=sheet_names.index(st.session_state.selected_sheet))
    st.session_state.selected_sheet = selected_sheet

    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()

    required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ Sheet must contain these columns: {required_columns}")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)
    df["Available Quantity"] = df["Available Quantity"].fillna(0).astype(int)

    st.session_state.df = df.copy()

# فنكشن تعالج الباركود بعد ما المستخدم يضغط submit
def process_barcode():
    scanned = st.session_state.barcode_input.strip()
    df = st.session_state.df

    if scanned:
        st.session_state.barcode_counts[scanned] = st.session_state.barcode_counts.get(scanned, 0) + 1

        if scanned in df["Barcodes"].values:
            count = st.session_state.barcode_counts[scanned]
            df.loc[df["Barcodes"] == scanned, "Actual Quantity"] = count
            st.session_state.product_name_display = df.loc[df["Barcodes"] == scanned, "Product Name"].values[0]
        else:
            st.session_state.product_name_display = "❌ Not Found"

        # Update DataFrame in session state
        st.session_state.df = df

        # Clear the input
        st.session_state.barcode_input = ""

# لو في ملف اتحمل خلاص
if st.session_state.df is not None:
    df = st.session_state.df

    st.markdown("### 📸 Scan Barcode")

    # Form عشان نتحكم في الإدخال
    with st.form("barcode_form", clear_on_submit=True):
        st.text_input("Scan Barcode", key="barcode_input")
        submitted = st.form_submit_button("Submit")
        if submitted:
            process_barcode()

    # Show product name
    st.markdown("#### 🏷️ Product Name")
    st.markdown(f"""
        <div style="padding: 0.75rem 1rem; background-color: #e6f4ea; border: 2px solid #2e7d32;
                    border-radius: 5px; font-weight: bold; font-size: 16px;">
            {st.session_state.product_name_display}
        </div>
    """, unsafe_allow_html=True)

    # Update Difference
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    st.subheader("📋 Updated Sheet")
    st.dataframe(df)

    # Log
    st.markdown("### ✅ Scanned Barcode Log")
    st.write(pd.DataFrame([
        {"Barcode": k, "Scanned Count": v}
        for k, v in st.session_state.barcode_counts.items()
    ]))

    # Download
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(df)
    st.download_button("📥 Download Updated Sheet", data=csv, file_name="updated_inventory.csv", mime="text/csv")
