import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# لتحميل ملف الإكسل
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet_choice = st.selectbox("Select Sheet", sheet_names)

    if sheet_choice:
        df = pd.read_excel(xls, sheet_name=sheet_choice)

        # التأكد من وجود الأعمدة المطلوبة
        required_columns = ["Barcodes", "Available Quantity"]
        if all(col in df.columns for col in required_columns):

            # تحويل العمود لسترينج لتسهيل المطابقة
            df["Barcodes"] = df["Barcodes"].astype(str)

            # جدول الإدخال
            st.subheader("Scan or Enter Barcode")
            if "barcode_input" not in st.session_state:
                st.session_state.barcode_input = ""

            barcode = st.text_input("Barcode", value=st.session_state.barcode_input, label_visibility="collapsed")

            # جدول لعرض النتائج المحدثة
            if "scanned_data" not in st.session_state:
                st.session_state.scanned_data = pd.DataFrame(columns=df.columns.tolist() + ["Actual Quantity", "Difference"])

            if barcode:
                match = df[df["Barcodes"] == barcode]
                if not match.empty:
                    row = match.iloc[0].to_dict()
                    row["Actual Quantity"] = 1

                    # لو الباركود اتسجل قبل كده
                    existing_index = st.session_state.scanned_data[st.session_state.scanned_data["Barcodes"] == barcode].index
                    if not existing_index.empty:
                        idx = existing_index[0]
                        st.session_state.scanned_data.at[idx, "Actual Quantity"] += 1
                    else:
                        st.session_state.scanned_data = pd.concat([
                            st.session_state.scanned_data,
                            pd.DataFrame([row])
                        ], ignore_index=True)

                    # إعادة تعيين حقل الإدخال بدون تغيير باقي الصفحة
                    st.experimental_rerun()

            # حساب الفروقات
            st.session_state.scanned_data["Difference"] = (
                st.session_state.scanned_data["Actual Quantity"] - st.session_state.scanned_data["Available Quantity"]
            )

            # عرض النتيجة
            st.subheader("Scanned Summary")
            st.dataframe(st.session_state.scanned_data, use_container_width=True)

        else:
            st.error("❌ Sheet must contain 'Barcodes' and 'Available Quantity' columns.")

else:
    st.info("⬆️ Please upload an Excel file to begin.")
