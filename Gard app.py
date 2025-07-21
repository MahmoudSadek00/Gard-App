import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع ملف الإكسل (يدعم ملفات متعددة الأوراق)
uploaded_file = st.file_uploader("Upload your inventory file (Excel with multiple sheets)", type=["xlsx"])

if uploaded_file:
    # قراءة جميع الأوراق في dict
    sheets_data = pd.read_excel(uploaded_file, sheet_name=None)

    if "sheets_data" not in st.session_state:
        st.session_state["sheets_data"] = sheets_data

# تأكد إن الملفات رفعت
if "sheets_data" in st.session_state:
    sheets_data = st.session_state["sheets_data"]

    # اختيار براند (ورقة)
    brand_selected = st.selectbox("Select Brand (Sheet)", options=list(sheets_data.keys()))

    df = sheets_data[brand_selected]

    # تحقق من وجود الأعمدة المطلوبة
    if not {"Barcodes", "Available Quantity"}.issubset(df.columns):
        st.error("❌ The sheet must have columns 'Barcodes' and 'Available Quantity'")
        st.stop()

    # جهز الأعمدة الجديدة لو مش موجودة
    if "Actual Quantity" not in df.columns:
        df["Actual Quantity"] = 0
    if "Difference" not in df.columns:
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    # حفظ الداتا المحدثة في session_state (مهم)
    st.session_state["sheets_data"][brand_selected] = df

    st.subheader(f"Brand: {brand_selected}")

    # تأكد من وجود المفتاح في session_state
    if "barcode_input" not in st.session_state:
        st.session_state["barcode_input"] = ""

    # حقل إدخال الباركود
    barcode = st.text_input("Scan or enter barcode:", key="barcode_input", placeholder="Type or scan barcode...")

    def process_barcode(barcode_value):
        barcode_value = barcode_value.strip()
        if len(barcode_value) >= 9:
            mask = df["Barcodes"].astype(str) == barcode_value
            if mask.any():
                df.loc[mask, "Actual Quantity"] += 1
                df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
                st.success(f"✅ Barcode '{barcode_value}' counted for brand '{brand_selected}'.")
            else:
                st.warning(f"❌ Barcode '{barcode_value}' not found in brand '{brand_selected}'.")
            # حدث الداتا في session_state بعد التغيير
            st.session_state["sheets_data"][brand_selected] = df
            return True
        return False

    # لما يدخل barcode و طوله كافي يعالج ويشيل قيمة الإدخال تلقائياً
    if barcode and process_barcode(barcode):
        st.session_state["barcode_input"] = ""

    # عرض جدول البراند المختار مع تحديثات الكميات
    st.dataframe(df, use_container_width=True)

    # تحميل الملف النهائي بجميع الأوراق، مع اسم يحتوي على البراند والتاريخ
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet_name, sheet_df in st.session_state["sheets_data"].items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()

    today_str = datetime.now().strftime("%Y-%m-%d")
    download_filename = f"Inventory_{today_str}.xlsx"

    st.download_button(
        label="📥 Download Updated Inventory File",
        data=buffer.getvalue(),
        file_name=download_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please upload an inventory Excel file to get started.")
