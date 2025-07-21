import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع الملف
uploaded_file = st.file_uploader("Upload your inventory file (Excel with multiple sheets)", type=["xlsx"])

if uploaded_file:
    # قراءة كل الشيتات
    sheets_data = pd.read_excel(uploaded_file, sheet_name=None)

    # حفظ البيانات في session_state لو مش موجودة أصلاً
    if "sheets_data" not in st.session_state:
        st.session_state.sheets_data = sheets_data

    # استخراج أسماء الشيتات (البراندات)
    brands = list(st.session_state.sheets_data.keys())

    # اختيار البراند من الدروب داون
    selected_brand = st.selectbox("Select Brand", brands)

    # استدعاء الداتا فريم المختارة
    df = st.session_state.sheets_data[selected_brand]

    # تحقق من الأعمدة المطلوبة
    required_cols = ["Barcodes", "Available Quantity"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"❌ Sheet '{selected_brand}' must contain columns: {required_cols}")
        st.stop()

    # اضف أعمدة لو مش موجودة
    if "Actual Quantity" not in df.columns:
        df["Actual Quantity"] = 0
    if "Difference" not in df.columns:
        # لا تعمل difference صيغة، احسبها على البايثون
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    st.session_state.sheets_data[selected_brand] = df  # تحديث الداتا

    # حقل إدخال الباركود (واحد فقط)
    barcode = st.text_input("Scan or type barcode", key="barcode_input", placeholder="Enter barcode here")

    # معالج الباركود
    if barcode and barcode.strip() != "":
        barcode_val = barcode.strip()
        if barcode_val in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode_val, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.success(f"✅ Barcode '{barcode_val}' counted successfully.")
            st.session_state.sheets_data[selected_brand] = df

            # تفريغ الحقل بدون rerun لتجنب أخطاء متكررة
            st.session_state.barcode_input = ""
        else:
            st.warning(f"❌ Barcode '{barcode_val}' not found in '{selected_brand}'.")

    # زر التحميل النهائي للملف مضافاً له تاريخ وبرانش (البرانش هنا البراند)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for brand_name, brand_df in st.session_state.sheets_data.items():
            # إعادة ترتيب الأعمدة لو تحب هنا (اختياري)
            cols_order = ["Barcodes", "Available Quantity", "Actual Quantity", "Difference"]
            cols_present = [col for col in cols_order if col in brand_df.columns]
            brand_df.to_excel(writer, sheet_name=brand_name[:31], index=False, columns=cols_present)
    buffer.seek(0)

    today_str = datetime.today().strftime("%Y-%m-%d")
    file_name = f"Inventory_{today_str}.xlsx"

    st.download_button(
        label="📥 Download Updated Inventory File",
        data=buffer,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # عرض جدول البيانات المحدث
    st.subheader(f"Inventory data for brand: {selected_brand}")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Please upload an Excel file with inventory data, containing multiple sheets for brands.")
