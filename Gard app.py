import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")

# حفظ البيانات في session state
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "sheet_name" not in st.session_state:
    st.session_state.sheet_name = None
if "df" not in st.session_state:
    st.session_state.df = None
if "barcode_input" not in st.session_state:
    st.session_state.barcode_input = ""

# رفع الملف
if st.session_state.uploaded_file is None:
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.experimental_rerun()  # إعادة تحميل الصفحة بعد الرفع

# لو الملف مرفوع
if st.session_state.uploaded_file is not None:

    # قراءة أسماء الشيتات
    xl = pd.ExcelFile(st.session_state.uploaded_file)
    sheet_names = xl.sheet_names

    # اختيار الشيت
    if st.session_state.sheet_name is None:
        st.session_state.sheet_name = sheet_names[0]

    sheet_name = st.selectbox("Select Sheet", sheet_names, index=sheet_names.index(st.session_state.sheet_name))
    st.session_state.sheet_name = sheet_name

    # قراءة البيانات من الشيت المحدد
    df = xl.parse(sheet_name)
    required_columns = ['Barcodes', 'Available Quantity', 'Product Name']

    if not all(col in df.columns for col in required_columns):
        st.error("Sheet must contain 'Barcodes', 'Available Quantity', and 'Product Name' columns.")
    else:
        # إنشاء عمود للكمية الفعلية
        if 'Actual Quantity' not in df.columns:
            df['Actual Quantity'] = 0

        st.session_state.df = df

        # إدخال الباركود
        barcode = st.text_input("Scan Barcode", key="barcode_input")

        if barcode:
            df = st.session_state.df
            matched = df['Barcodes'] == barcode

            if matched.any():
                df.loc[matched, 'Actual Quantity'] += 1
                st.session_state.df = df
            else:
                st.warning("Barcode not found in the list.")

            # تهيئة خانة الإدخال
            st.session_state.barcode_input = ""
            st.experimental_rerun()

        # عرض الجدول
        st.dataframe(st.session_state.df)

        # تحميل ملف الإكسل المحدث
        with pd.ExcelWriter("updated_inventory.xlsx", engine="xlsxwriter") as writer:
            st.session_state.df.to_excel(writer, sheet_name="Updated", index=False)
        with open("updated_inventory.xlsx", "rb") as f:
            st.download_button("📥 Download Updated Excel", f, file_name="updated_inventory.xlsx")
