import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Barcode Scanner")

# تحميل ملف الإكسل
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    # قراءة كل الـ sheets مرة واحدة
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheets_data = {name: xls.parse(name) for name in sheet_names}

    # اختيار الشيت (البراند) من Dropdown
    selected_sheet = st.selectbox("Select a brand sheet:", sheet_names)

    # الشيت اللي اختاره المستخدم
    df = sheets_data[selected_sheet]

    # تأكد من وجود الأعمدة المطلوبة
    if "Barcodes" in df.columns and "Available Quantity" in df.columns:
        # باركود سكان سريع
        barcode = st.text_input("Scan or enter barcode")

        if "scanned" not in st.session_state:
            st.session_state.scanned = {}

        # تحديث الكمية لو الباركود متسجل
        if barcode:
            if barcode in df["Barcodes"].astype(str).values:
                if barcode not in st.session_state.scanned:
                    st.session_state.scanned[barcode] = 1
                else:
                    st.session_state.scanned[barcode] += 1
                st.experimental_rerun()  # إعادة تحميل الصفحة تلقائيًا بعد كل إدخال

        # إنشاء DataFrame من الباركودات اللي تم سكانها
        scanned_df = pd.DataFrame.from_dict(st.session_state.scanned, orient="index", columns=["Actual Quantity"])
        scanned_df.reset_index(inplace=True)
        scanned_df.rename(columns={"index": "Barcodes"}, inplace=True)

        # دمج الداتا الأصلية مع السكان
        merged = pd.merge(df, scanned_df, on="Barcodes", how="left")
        merged["Actual Quantity"] = merged["Actual Quantity"].fillna(0).astype(int)
        merged["Difference"] = merged["Actual Quantity"] - merged["Available Quantity"]

        st.subheader("📊 Updated Inventory")
        st.dataframe(merged)

        # تحميل الناتج
        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df_to_csv(merged)
        st.download_button("📥 Download CSV", data=csv, file_name="updated_inventory.csv", mime="text/csv")

    else:
        st.error("❌ Required columns 'Barcodes' and 'Available Quantity' not found in selected sheet.")
else:
    st.info("⬆️ Please upload an Excel file to begin.")
