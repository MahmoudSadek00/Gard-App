import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع الملف مع قراءة جميع الشيتات
uploaded_file = st.file_uploader("Upload your inventory file (Excel with multiple sheets)", type=["xlsx"])

if uploaded_file:
    try:
        # قراءة كل الشيتات في dict
        sheets_dict = pd.read_excel(uploaded_file, sheet_name=None)
        st.session_state.sheets_data = sheets_dict
        # تحديد قائمة البراندات من أسماء الشيتات
        brand_list = list(sheets_dict.keys())
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    brand_list = []

if brand_list:
    selected_brand = st.selectbox("Select Brand", brand_list)

    df = st.session_state.sheets_data[selected_brand]

    # تأكد من الأعمدة المطلوبة
    required_cols = ["Barcodes", "Available Quantity"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"⚠️ Missing required column '{col}' in sheet '{selected_brand}'")
            st.stop()

    # إذا ما كان في عمود "Actual Quantity" ضيفه
    if "Actual Quantity" not in df.columns:
        df["Actual Quantity"] = 0

    # أظهر خانة باركود
    barcode = st.text_input("Scan or enter barcode", key="barcode_input")

    if barcode and len(barcode.strip()) >= 9:
        barcode = barcode.strip()
        # تحديث Actual Quantity أوتوماتيكي
        matches = df["Barcodes"].astype(str) == barcode
        if matches.any():
            df.loc[matches, "Actual Quantity"] += 1
            st.success(f"✅ Barcode {barcode} counted for brand {selected_brand}")
        else:
            st.warning(f"❌ Barcode {barcode} not found in brand {selected_brand}")

        # تحديث الفرق
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

        # فرغ خانة الإدخال
        st.session_state["barcode_input"] = ""
        st.experimental_rerun()

    # حساب الفرق لو مش موجود
    if "Difference" not in df.columns:
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    st.dataframe(df, use_container_width=True)

    # تحميل الملف بعد التحديث
    buffer = io.BytesIO()
    today_str = datetime.today().strftime("%Y-%m-%d")
    file_name = f"{selected_brand}_{today_str}_inventory.xlsx"

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for brand_name, brand_df in st.session_state.sheets_data.items():
            # لو نفس البراند اللي شغال عليه حدثنا العمود "Actual Quantity" و "Difference"
            if brand_name == selected_brand:
                brand_df = df
            else:
                # إذا ما فيه عمود "Actual Quantity" ضيفه وصفر
                if "Actual Quantity" not in brand_df.columns:
                    brand_df["Actual Quantity"] = 0
                if "Difference" not in brand_df.columns:
                    brand_df["Difference"] = brand_df["Actual Quantity"] - brand_df["Available Quantity"]

            brand_df.to_excel(writer, sheet_name=brand_name, index=False)

    st.download_button(
        label="📥 Download Updated Inventory File",
        data=buffer.getvalue(),
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
