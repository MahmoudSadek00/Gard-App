import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory App", layout="wide")
st.title("📦 Domanza Inventory App")

# تهيئة session state
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "sheets" not in st.session_state:
    st.session_state.sheets = []
if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None

# رفع الملف
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file
    xls = pd.ExcelFile(uploaded_file)
    st.session_state.sheets = xls.sheet_names

# اختيار الشيت
if st.session_state.sheets:
    selected_sheet = st.selectbox("Select Brand Sheet", st.session_state.sheets, index=0)
    st.session_state.selected_sheet = selected_sheet

# تحميل الداتا من الشيت
if st.session_state.uploaded_file and st.session_state.selected_sheet:
    df = pd.read_excel(st.session_state.uploaded_file, sheet_name=st.session_state.selected_sheet)
    
    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()

    # إنشاء العمود لو مش موجود
    if "Actual Quantity" not in df.columns:
        df["Actual Quantity"] = 0

    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)

    # إدخال الباركود
    barcode = st.text_input("🔍 Scan or Enter Barcode", key="barcode_input")

    if barcode:
        barcode = barcode.strip()
        matches = df[df["Barcodes"] == barcode].index.tolist()

        if matches:
            idx = matches[0]
            df.at[idx, "Actual Quantity"] += 1
            st.success(f"✅ Updated Actual Quantity for: {barcode}")
        else:
            st.error(f"❌ Barcode {barcode} not found in selected sheet.")

        # مسح خانة الباركود بعد الضرب
        st.session_state.barcode_input = ""

    # عرض الجدول
    st.dataframe(df)
