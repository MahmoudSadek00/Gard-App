import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# إعداد session state
if 'scanned_barcodes' not in st.session_state:
    st.session_state.scanned_barcodes = []

# رفع ملف الإكسل
uploaded_file = st.file_uploader("ارفع ملف الجرد (Excel فقط)", type=["xlsx"])

# اختيار الشيت
if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())

    selected_sheet = st.selectbox("اختر البراند (Sheet)", sheet_names)
    df = all_sheets[selected_sheet]
    df = df.rename(columns=lambda x: x.strip())

    if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
        st.error("لازم يكون في عمود 'Barcodes' و 'Available Quantity' في الشيت")
        st.stop()

    # كاميرا الباركود (مربع الإدخال)
    st.markdown("### 📸 اسكان الباركود بالكاميرا أو الموبايل")
    barcode_input = st.text_input("👈 اسكان الباركود هنا", value="", label_visibility="collapsed")

    # تحديث الباركودات
    if barcode_input:
        st.session_state.scanned_barcodes.append(barcode_input)
        st.experimental_rerun()

    # تجهيز DataFrame للباركودات
    scanned_df = pd.DataFrame(st.session_state.scanned_barcodes, columns=["Barcodes"])
    scanned_df["Actual Quantity"] = 1
    scanned_df = scanned_df.groupby("Barcodes").sum().reset_index()

    # Merge لما يبقى في سكان فعلي
    if not scanned_df.empty:
        merged = pd.merge(df, scanned_df, on="Barcodes", how="left")
        merged["Actual Quantity"] = merged["Actual Quantity"].fillna(0).astype(int)
        merged["Difference"] = merged["Actual Quantity"] - merged["Available Quantity"]

        st.subheader("📊 النتائج بعد الاسكان")
        st.dataframe(merged)

        # زر تحميل النتائج
        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode("utf-8")

        csv = convert_df_to_csv(merged)
        st.download_button("📥 تحميل النتائج كـ CSV", data=csv, file_name="updated_inventory.csv", mime="text/csv")
    else:
        st.info("👀 منتظرين سكان باركود...")
