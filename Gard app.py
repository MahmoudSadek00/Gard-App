import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inventory Scanner", layout="wide")

# إخفاء خانة الرفع بعد الرفع
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None

if not st.session_state.uploaded:
    file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])
    if file:
        xls = pd.ExcelFile(file)
        st.session_state.sheets = xls.sheet_names
        st.session_state.df_dict = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
        st.session_state.uploaded = True
        st.rerun()

# اختيار البراند (الشيت)
if st.session_state.uploaded:
    sheet_name = st.selectbox("Select Brand Sheet", st.session_state.sheets)
    df = st.session_state.df_dict[sheet_name]

    # التأكد من وجود العمودين
    if 'Barcodes' not in df.columns or 'Actual Quantity' not in df.columns:
        st.error("Sheet must contain 'Barcodes' and 'Actual Quantity' columns.")
        st.stop()

    if "barcode_input" not in st.session_state:
        st.session_state.barcode_input = ""

    # إدخال الباركود
    barcode = st.text_input("Scan or Enter Barcode", value=st.session_state.barcode_input, key="barcode_field")

    # عرض جدول الجرد
    st.dataframe(df)

    # تحديث الكمية تلقائيًا عند مسح الباركود
    if barcode:
        barcode = barcode.strip()
        matches = df[df["Barcodes"] == barcode].index.tolist()

        if matches:
            idx = matches[0]
            current_value = df.at[idx, "Actual Quantity"]
            df.at[idx, "Actual Quantity"] = current_value + 1 if pd.notna(current_value) else 1
            st.success(f"✅ Updated quantity for barcode: {barcode}")
        else:
            st.warning(f"❌ Barcode {barcode} not found in selected sheet.")

        st.session_state.barcode_input = ""  # تفريغ خانة الإدخال
        st.rerun()

    # زر لحفظ الملف المعدل (اختياري)
    if st.button("Download Updated Sheet"):
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet, data in st.session_state.df_dict.items():
                data.to_excel(writer, sheet_name=sheet, index=False)
            writer.save()
        st.download_button(label="📥 Download Excel", data=output.getvalue(),
                           file_name="updated_inventory.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
