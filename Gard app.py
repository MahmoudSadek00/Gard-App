import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Barcode Scanner")

# تحميل ملف الإكسل
uploaded_file = st.file_uploader("⬆️ Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    # قراءة الملف وجلب أسماء الشيتات
    xls = pd.ExcelFile(uploaded_file)
    sheets = xls.sheet_names

    # حفظ أسماء الشيتات في session_state لمرة واحدة
    if "sheets" not in st.session_state:
        st.session_state.sheets = sheets

    # اختيار الشيت
    sheet_name = st.selectbox("📄 Select Brand Sheet", st.session_state.sheets)

    df = pd.read_excel(xls, sheet_name=sheet_name)

    # التأكد من وجود الأعمدة المطلوبة
    if "Barcodes" not in df.columns or "Actual Quantity" not in df.columns:
        st.error("❌ Sheet must contain 'Barcodes' and 'Actual Quantity' columns.")
    else:
        # إدخال الباركود
        barcode = st.text_input("🔍 Scan or Enter Barcode", key="barcode_input")

        if barcode:
            if barcode in df["Barcodes"].astype(str).values:
                idx = df[df["Barcodes"].astype(str) == barcode].index[0]
                
                # التأكد إن القيمة مش None
                current_qty = df.at[idx, "Actual Quantity"]
                if pd.isna(current_qty):
                    current_qty = 0

                # زيادة الكمية واحدة
                df.at[idx, "Actual Quantity"] = current_qty + 1

                st.success(f"✅ Barcode {barcode} found! Count updated to {current_qty + 1}")
            else:
                st.error(f"❌ Barcode {barcode} not found in selected sheet.")

            st.rerun()

        # عرض الجدول
        st.dataframe(df)

        # تنزيل الملف بعد التحديث
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        st.download_button("⬇️ Download Updated Sheet", data=output.getvalue(), file_name="updated_inventory.xlsx")
