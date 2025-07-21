import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner App", layout="centered")
st.title("📦 Inventory Scanner App")

# مرحلة رفع الملف
if "df" not in st.session_state:
    uploaded_file = st.file_uploader("⬆️ Upload inventory file (Excel or CSV)", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # تأكد من الأعمدة المطلوبة
            if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
                st.error("❌ الملف لازم يحتوي على العمودين: 'Barcodes' و 'Available Quantity'")
                st.stop()

            # إضافة الأعمدة
            df["Actual Quantity"] = 0
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state.df = df
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
    else:
        st.stop()

# مرحلة سكان الباركود
else:
    df = st.session_state.df
    st.subheader("🔍 Scan Barcode")

    barcode = st.text_input("📷 Scan barcode here", value="", key="barcode_input")

    if barcode:
        barcode = barcode.strip()
        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.success(f"✅ Barcode scanned: {barcode}")
        else:
            st.warning(f"⚠️ Barcode not found: {barcode}")
        st.session_state.barcode_input = ""

    # عرض الجدول
    st.dataframe(df, use_container_width=True)

    # زر تحميل الملف
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        "📥 Download updated inventory file",
        data=buffer.getvalue(),
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
