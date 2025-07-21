import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

def clear_barcode():
    st.session_state.barcode_input = ""

# رفع الملف
uploaded_file = st.file_uploader("Upload your inventory file (Excel with multiple sheets)", type=["xlsx"])
if not uploaded_file:
    st.info("Please upload an Excel file with inventory sheets per brand.")
    st.stop()

# قراءة كل الشيتات في dict
try:
    sheets_data = pd.read_excel(uploaded_file, sheet_name=None)
except Exception as e:
    st.error(f"Error reading Excel file: {e}")
    st.stop()

# حفظ sheets_data في session_state إذا مش موجودة
if "sheets_data" not in st.session_state:
    # لكل شيت، تأكد فيه أعمدة Barcodes و Available Quantity، وأضف Actual Quantity و Difference
    clean_sheets = {}
    for sheet_name, df in sheets_data.items():
        if not all(col in df.columns for col in ["Barcodes", "Available Quantity"]):
            st.warning(f"Sheet '{sheet_name}' missing 'Barcodes' or 'Available Quantity' columns. Ignored.")
            continue
        df["Actual Quantity"] = 0
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
        clean_sheets[sheet_name] = df
    st.session_state.sheets_data = clean_sheets

if len(st.session_state.sheets_data) == 0:
    st.error("No valid sheets with required columns found.")
    st.stop()

# اختيار براند من الدروبداون
selected_brand = st.selectbox("Select Brand", options=list(st.session_state.sheets_data.keys()))

df = st.session_state.sheets_data[selected_brand]

# خانة إدخال الباركود (تمسح نفسها تلقائياً بعد كل إدخال)
barcode = st.text_input(
    "Scan or enter barcode",
    key="barcode_input",
    placeholder="Scan or type barcode here",
    on_change=clear_barcode,
)

# تحديث البيانات عند وجود باركود
if barcode and barcode.strip() != "":
    barcode_val = barcode.strip()
    if barcode_val in df["Barcodes"].astype(str).values:
        df.loc[df["Barcodes"].astype(str) == barcode_val, "Actual Quantity"] += 1
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
        st.success(f"✅ Barcode '{barcode_val}' counted successfully.")
        st.session_state.sheets_data[selected_brand] = df  # تحديث session_state
    else:
        st.warning(f"❌ Barcode '{barcode_val}' not found in '{selected_brand}'.")

# عرض الجدول
st.subheader(f"Inventory for {selected_brand}")
st.dataframe(df, use_container_width=True)

# زر تحميل الملف النهائي مع اسم براند + تاريخ اليوم
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    for sheet, sheet_df in st.session_state.sheets_data.items():
        sheet_df.to_excel(writer, sheet_name=sheet[:31], index=False)
    writer.save()
buffer.seek(0)

today_str = datetime.today().strftime("%Y-%m-%d")
filename = f"Inventory_{today_str}.xlsx"

st.download_button(
    label="📥 Download Updated Inventory Excel",
    data=buffer,
    file_name=filename,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
