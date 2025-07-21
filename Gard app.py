import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع الملف
uploaded_file = st.file_uploader("Upload your inventory file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # تأكد من وجود الأعمدة المطلوبة
        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("⚠️ File must include 'Barcodes' and 'Available Quantity' columns.")
            st.stop()

        # أضف عمود 'Actual Quantity' إذا مش موجود
        if "Actual Quantity" not in df.columns:
            df["Actual Quantity"] = 0

        # احفظ البيانات في الجلسة
        st.session_state["df"] = df

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

if "df" in st.session_state:
    df = st.session_state["df"]

    st.subheader("📸 Scan Barcode")

    # تأكد من وجود المفتاح في session_state
    if "barcode_input" not in st.session_state:
        st.session_state["barcode_input"] = ""

    # حقل الإدخال
    barcode = st.text_input("Scan or enter barcode (9 digits)", key="barcode_input")

    if barcode and len(barcode) == 9:
        barcode = barcode.strip()
        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state["df"] = df
            st.success(f"✅ Barcode {barcode} counted.")
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

        # امسح حقل الإدخال بدون استخدام rerun()
        st.session_state["barcode_input"] = ""

    st.dataframe(df, use_container_width=True)

    # زر تحميل الملف المعدل
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")
        writer.save()

    st.download_button(
        label="📥 Download Updated Inventory",
        data=buffer.getvalue(),
        file_name=f"Inventory_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
