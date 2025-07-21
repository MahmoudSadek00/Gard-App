import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Gard Inventory Scanner", layout="wide")

st.title("📦 Gard Inventory Scanner")

# التحقق من تحميل الملف
uploaded_file = st.file_uploader("Upload the inventory file", type=["csv", "xlsx"])

# تهيئة session_state
if "barcode_input" not in st.session_state:
    st.session_state.barcode_input = ""
if "clear_flag" not in st.session_state:
    st.session_state.clear_flag = False

# تنفيذ المسح لو clear_flag مرفوع
if st.session_state.clear_flag:
    st.session_state.barcode_input = ""
    st.session_state.clear_flag = False
    st.experimental_rerun()

# تحميل البيانات
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # عرض الجدول
    st.dataframe(df)

    # إدخال الباركود
    st.subheader("Scan or Enter Barcode")

    st.session_state.barcode_input = st.text_input("Barcode", value=st.session_state.barcode_input, label_visibility="collapsed")

    # البحث عن الباركود
    if st.button("✅ Confirm"):
        sca = st.session_state.barcode_input.strip()
        if sca in df["Barcodes"].astype(str).values:
            idx = df[df["Barcodes"].astype(str) == sca].index[0]
            df.at[idx, "Available Quantity"] += 1
            st.success("✅ Quantity Updated")
        else:
            st.warning("❌ Barcode Not Found")

    # زرار المسح
    if st.button("🧹 Clear"):
        st.session_state.clear_flag = True
        st.experimental_rerun()

    # عرض النتيجة بعد التحديث
    st.subheader("📊 Updated Table")
    st.dataframe(df)
else:
    st.info("📤 Please upload an inventory file to begin.")
