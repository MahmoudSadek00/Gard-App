import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App")

# تحميل الملف
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

# تهيئة الحالة
if 'scanned_barcodes' not in st.session_state:
    st.session_state.scanned_barcodes = []
if 'product_name_display' not in st.session_state:
    st.session_state.product_name_display = ""
if 'inventory_df' not in st.session_state:
    st.session_state.inventory_df = None

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.selectbox("Select Sheet", sheet_names)

    if st.session_state.inventory_df is None:
        df = all_sheets[selected_sheet]
        df.columns = df.columns.str.strip()
        df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
        df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)
        st.session_state.inventory_df = df

    df = st.session_state.inventory_df

    required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
    if any(col not in df.columns for col in required_columns):
        st.error("❌ Missing required columns.")
        st.stop()

    # Scan barcode input
    st.markdown("### 📸 Scan Barcode")
    barcode_input = st.text_input("Scan Here", key="barcode_input")

    if barcode_input:
        barcode = barcode_input.strip()
        st.session_state.scanned_barcodes.append(barcode)

        mask = df["Barcodes"] == barcode
        if mask.any():
            df.loc[mask, "Actual Quantity"] += 1
            st.session_state.product_name_display = df.loc[mask, "Product Name"].values[0]
        else:
            st.session_state.product_name_display = "❌ Not Found"

        st.session_state.barcode_input = ""  # لتفريغ الخانة
        st.experimental_rerun()

    # خانة اسم المنتج (مقفولة ومنورة)
    st.text_input("Product Name", value=st.session_state.product_name_display, disabled=True, label_visibility="visible")

    # الفروقات
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    # عرض الجدول
    st.subheader("📋 Updated Inventory")
    st.dataframe(df)

    # تحميل
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(df)
    st.download_button("📥 Download CSV", data=csv, file_name="updated_inventory.csv", mime="text/csv")
