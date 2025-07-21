import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# إعدادات الجلسة
if 'scanned_barcodes' not in st.session_state:
    st.session_state.scanned_barcodes = []
if 'product_name_display' not in st.session_state:
    st.session_state.product_name_display = ""

# رفع الملف
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names)
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()

    required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"❌ Sheet must contain: {', '.join(required_columns)}")
        st.stop()

    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)

    # Scan barcode input
    st.markdown("### 📸 Scan Barcode")
    barcode_input = st.text_input("Scan Here", key="barcode_input")

    if barcode_input:
        barcode = barcode_input.strip()
        st.session_state.scanned_barcodes.append(barcode)

        # تحديث الكمية
        mask = df["Barcodes"] == barcode
        if mask.any():
            df.loc[mask, "Actual Quantity"] += 1
            st.session_state.product_name_display = df.loc[mask, "Product Name"].values[0]
        else:
            st.session_state.product_name_display = "❌ Not Found"

        # تفريغ الخانة بإعادة تشغيل الصفحة
        st.experimental_rerun()

    # خانة اسم المنتج (بارزة ومقفولة)
    st.text_input("Product Name", value=st.session_state.product_name_display, disabled=True, label_visibility="visible")

    # الفروق
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    # جدول العرض
    st.subheader("📋 Updated Inventory")
    st.dataframe(df)

    # التحميل
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(df)
    st.download_button("📥 Download Updated Sheet", data=csv, file_name="updated_inventory.csv", mime="text/csv")
