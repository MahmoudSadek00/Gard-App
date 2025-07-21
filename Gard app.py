import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع الملف (Excel أو CSV)
uploaded_file = st.file_uploader("Upload your inventory file", type=["csv", "xlsx"])

if uploaded_file and "sheets_data" not in st.session_state:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.session_state.sheets_data = {"Sheet1": df}  # CSV له ورقة واحدة
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheets = {}
            for sheet_name in xls.sheet_names:
                sheets[sheet_name] = xls.parse(sheet_name)
            st.session_state.sheets_data = sheets

        # تحقق وجود أعمدة أساسية في كل شيت
        for sheet_name, df in st.session_state.sheets_data.items():
            if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
                st.error(f"⚠️ Sheet '{sheet_name}' must include 'Barcodes' and 'Available Quantity' columns.")
                st.stop()

            if "Actual Quantity" not in df.columns:
                df["Actual Quantity"] = 0
            if "Difference" not in df.columns:
                df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state.sheets_data[sheet_name] = df

        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

if "sheets_data" in st.session_state:
    sheets_data = st.session_state.sheets_data

    # اختيار براند (اسم الشيت)
    selected_sheet = st.selectbox("Select Brand (Sheet)", options=list(sheets_data.keys()))

    df = sheets_data[selected_sheet]

    # خانة إدخال الباركود (يدوي أو من الكاميرا)
    barcode = st.text_input("Scan or enter barcode", key="barcode_input")

    if barcode:
        barcode = barcode.strip()
        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.success(f"✅ Barcode {barcode} counted.")
            # مسح خانة الإدخال
            st.session_state["barcode_input"] = ""
            # تحديث البيانات في ال session state
            st.session_state.sheets_data[selected_sheet] = df
            st.experimental_rerun()
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

    # عرض جدول البيانات
    st.dataframe(df, use_container_width=True)

    # زر تحميل الملف النهائي
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet_name, sheet_df in sheets_data.items():
            # تحديث الفرق في كل شيت قبل الحفظ
            sheet_df["Difference"] = sheet_df["Actual Quantity"] - sheet_df["Available Quantity"]
            sheet_df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    buffer.seek(0)

    today = datetime.today().strftime("%Y-%m-%d")
    file_name = f"Inven_
