import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="📦 Inventory Scanner", layout="centered")

# رفع ملف المنتجات
uploaded_file = st.file_uploader("Upload Inventory File", type=["xlsx", "xls", "csv"])
if uploaded_file is None:
    st.stop()

# قراءة البيانات
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# التحقق من الأعمدة الأساسية
required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
for col in required_columns:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# تهيئة الحالة
if "scanned_barcodes" not in st.session_state:
    st.session_state.scanned_barcodes = []
if "product_name_display" not in st.session_state:
    st.session_state.product_name_display = ""

st.markdown("### 📸 Scan Product")

# باركود إنبوت
barcode = st.text_input("Scan Barcode", key="barcode_input", placeholder="Scan barcode...", label_visibility="visible")

# عرض اسم المنتج (غير قابل للتعديل)
st.text_input("Product Name", value=st.session_state.product_name_display, disabled=True, key="product_name_display_field", label_visibility="visible")

# لو تم إدخال باركود
if barcode:
    barcode_clean = barcode.strip()
    st.session_state.scanned_barcodes.append(barcode_clean)

    # تحديث الكمية الفعلية
    mask = df["Barcodes"] == barcode_clean
    if mask.any():
        df.loc[mask, "Actual Quantity"] += 1
        st.session_state.product_name_display = df.loc[mask, "Product Name"].values[0]
    else:
        st.session_state.product_name_display = "❌ Not Found"

    # إعادة ضبط الخانة
    st.session_state["barcode_input"] = ""
    st.experimental_rerun()

# عرض الجدول (اختياري)
with st.expander("📋 Current Inventory", expanded=False):
    st.dataframe(df, use_container_width=True)

# تحميل الملف بعد الجرد (اختياري)
@st.cache_data
def convert_df_to_excel(dataframe):
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Inventory")
    output.seek(0)
    return output

excel_data = convert_df_to_excel(df)
st.download_button("📥 Download Updated Inventory", data=excel_data, file_name="updated_inventory.xlsx")
