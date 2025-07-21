import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory Application")

# تحميل ملف الإكسل
uploaded_file = st.file_uploader("⬆️ Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    # قراءة الملف
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    # اختيار الشيت
    selected_sheet = st.selectbox("اختر الشيت:", sheet_names)

    if selected_sheet:
        df = xls.parse(selected_sheet)

        # تنظيف أسماء الأعمدة
        df.columns = df.columns.astype(str).str.strip()
        df.columns = df.columns.str.replace('“|”|\"|\'', '', regex=True)

        # طباعة الأعمدة الحقيقية
        st.write("📋 Actual columns read:", df.columns.tolist())

        # التحقق من الأعمدة المطلوبة
        if not {"Barcodes", "Available Quantity"}.issubset(df.columns):
            st.error("❌ الشيت لازم يحتوي على الأعمدة: Barcodes و Available Quantity")
            st.stop()

        # إنشاء session state للبيانات الممسوحة
        if "scanned_data" not in st.session_state:
            st.session_state.scanned_data = pd.DataFrame(columns=["Barcodes", "Available Quantity", "Actual Quantity"])

        # إدخال الباركود
        barcode_input = st.text_input("🧪 Scan Barcode", key="barcode_input")

        # تحديث الجدول عند إدخال باركود
        if barcode_input:
            match = df[df["Barcodes"].astype(str) == barcode_input]
            if not match.empty:
                qty = st.number_input("📝 Actual Quantity", min_value=0, step=1, key="qty_input")
                if st.button("➕ Add"):
                    new_row = {
                        "Barcodes": barcode_input,
                        "Available Quantity": int(match["Available Quantity"].values[0]),
                        "Actual Quantity": qty
                    }
                    st.session_state.scanned_data = pd.concat(
                        [st.session_state.scanned_data, pd.DataFrame([new_row])],
                        ignore_index=True
                    )
                    st.experimental_rerun()
            else:
                st.warning("❌ الباركود غير موجود في الشيت.")

        # عرض البيانات الممسوحة
        if not st.session_state.scanned_data.empty:
            st.dataframe(st.session_state.scanned_data, use_container_width=True)

            # تحميل البيانات النهائية
            def convert_df(df):
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
                df.to_excel(writer, index=False, sheet_name='Scanned Data')
                writer.close()
                output.seek(0)
                return output

            st.download_button(
                label="⬇️ Download Results",
                data=convert_df(st.session_state.scanned_data),
                file_name="scanned_inventory.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # زرار للمسح
        if st.button("🧹 Clear All"):
            st.session_state.scanned_data = pd.DataFrame(columns=["Barcodes", "Available Quantity", "Actual Quantity"])
            st.experimental_rerun()
