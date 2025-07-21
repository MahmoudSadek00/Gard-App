import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع الملف
uploaded_file = st.file_uploader("Upload your inventory file (Excel with multiple sheets)", type=["xlsx"])

if uploaded_file:
    if "sheets_data" not in st.session_state:
        # اقرأ كل الشيتات في dict
        xls = pd.ExcelFile(uploaded_file)
        sheets_data = {}
        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            # تحقق من الأعمدة المطلوبة
            if not {"Barcodes", "Available Quantity", "Actual Quantity"}.issubset(df.columns):
                st.error(f"Sheet '{sheet_name}' must contain 'Barcodes', 'Available Quantity', and 'Actual Quantity' columns.")
                st.stop()
            # تحديث عمود Difference
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            sheets_data[sheet_name] = df
        st.session_state["sheets_data"] = sheets_data
        st.session_state["selected_sheet"] = xls.sheet_names[0]
        st.session_state["barcode_input"] = ""

# اختيار الشيت
if "sheets_data" in st.session_state:
    sheets_data = st.session_state["sheets_data"]
    selected_sheet = st.selectbox("Select Brand Sheet", list(sheets_data.keys()), index=list(sheets_data.keys()).index(st.session_state.get("selected_sheet", list(sheets_data.keys())[0])))
    st.session_state["selected_sheet"] = selected_sheet
    df = sheets_data[selected_sheet]

    # خانة السكان والادخال (كتابة أو نسخ باركود)
    barcode = st.text_input("Scan or enter barcode:", value=st.session_state.get("barcode_input", ""), key="barcode_input")

    if barcode and len(barcode.strip()) >= 9:
        barcode = barcode.strip()
        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            sheets_data[selected_sheet] = df
            st.session_state["sheets_data"] = sheets_data
            st.success(f"✅ Barcode '{barcode}' counted.")
        else:
            st.warning(f"❌ Barcode '{barcode}' not found in sheet '{selected_sheet}'.")
        # بعد التحديث امسح القيمة وخليها جاهزة للسكان التالي
        st.session_state["barcode_input"] = ""
        st.experimental_rerun()

    st.dataframe(df, use_container_width=True)

    # تحديث فرق الكميات لكل شيت قبل الحفظ
    for sheet_name in sheets_data:
        df_temp = sheets_data[sheet_name]
        df_temp["Difference"] = df_temp["Actual Quantity"] - df_temp["Available Quantity"]
        sheets_data[sheet_name] = df_temp
    st.session_state["sheets_data"] = sheets_data

    # تحميل الملف المعدل
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet_name, sheet_df in sheets_data.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    today_str = datetime.now().strftime("%Y-%m-%d")
    download_filename = f"Inventory_{today_str}.xlsx"

    st.download_button(
        label="📥 Download Updated Inventory File",
        data=buffer.getvalue(),
        file_name=download_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
