import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Session state
if 'scanned_barcodes' not in st.session_state:
    st.session_state.scanned_barcodes = []

# File uploader
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names)
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()

    # التحقق من الأعمدة المطلوبة
    required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"❌ Sheet must contain: {', '.join(required_columns)}")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    # تنظيف الأعمدة
    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)

    # 📸 سكان باركود
    st.markdown("### 📸 Scan Barcode")
    barcode_input = st.text_input("Scan Here", value="", label_visibility="visible")

    product_name_display = ""
    if barcode_input:
        barcode_input = barcode_input.strip()
        st.session_state.scanned_barcodes.append(barcode_input)

        # تحديث الكمية في الشيت الأصلي
        existing = df["Barcodes"] == barcode_input
        if existing.any():
            df.loc[existing, "Actual Quantity"] += 1
            product_name_display = df.loc[existing, "Product Name"].values[0]
        else:
            product_name_display = "❌ Not Found"

    # 👇 عرض اسم المنتج تحت الباركود بنفس الشكل وبوضوح
    st.text_input("Product Name", value=product_name_display, disabled=True, label_visibility="visible")

    # حساب الفرق
    if "Difference" not in df.columns:
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
    else:
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    # عرض البيانات
    st.subheader("📋 Updated Sheet")
    st.dataframe(df)

    # تحويل CSV
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(df)
    st.download_button("📥 Download Updated Sheet", data=csv, file_name="updated_inventory.csv", mime="text/csv")
