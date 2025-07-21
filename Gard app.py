import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع الملف
uploaded_file = st.file_uploader("Upload your inventory Excel file", type=["xlsx", "xls"])

if uploaded_file:
    # قراءة جميع الشيتات في dict
    sheets_data = pd.read_excel(uploaded_file, sheet_name=None)

    # محاولة استخراج أسماء البراندات من اسماء الشيتات أو من عمود Branch
    brands = list(sheets_data.keys())

    # اختيار البراند (الشيت) من Dropdown
    selected_brand = st.selectbox("Select Brand (Sheet)", brands)

    if selected_brand:
        df = sheets_data[selected_brand]

        # تأكد الأعمدة المطلوبة موجودة
        expected_cols = ['Barcodes', 'Available Quantity', 'Branch']
        missing = [col for col in expected_cols if col not in df.columns]
        if missing:
            st.error(f"Missing columns in sheet '{selected_brand}': {missing}")
            st.stop()

        # إضافة Actual Quantity وفارق Difference
        if 'Actual Quantity' not in df.columns:
            df['Actual Quantity'] = 0
        df['Difference'] = df['Actual Quantity'] - df['Available Quantity']

        # خانة السكان تحت Dropdown البراند
        barcode_input = st.text_input("Scan or enter barcode")

        if barcode_input:
            barcode = barcode_input.strip()
            if barcode in df['Barcodes'].astype(str).values:
                df.loc[df['Barcodes'].astype(str) == barcode, 'Actual Quantity'] += 1
                df['Difference'] = df['Actual Quantity'] - df['Available Quantity']
                st.success(f"Barcode {barcode} counted.")
            else:
                st.warning(f"Barcode '{barcode}' not found.")

            # إعادة ضبط حقل الإدخال
            st.experimental_rerun()

        # زرار تشغيل وإيقاف الكاميرا (لأننا ما دمجناش الكاميرا هنا ممكن تضيف لاحقًا)
        st.button("Toggle Camera (Add later)")

        # عرض بيانات الشيت المختار
        st.subheader(f"Inventory Sheet: {selected_brand}")
        st.dataframe(df, use_container_width=True)

        # تجهيز الملف للتحميل بالاسم المطلوب
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name=selected_brand)
            writer.save()

        # اسم الملف: فرع + تاريخ اليوم
        today_str = datetime.today().strftime("%Y-%m-%d")
        # لو عمود Branch فيه قيم مختلفة ناخد أول قيمة (ممكن تعدل حسب حاجتك)
        branch_val = df['Branch'].iloc[0] if 'Branch' in df.columns and not df['Branch'].empty else 'Branch'
        safe_branch_val = str(branch_val).replace(" ", "_")

        file_name = f"{safe_branch_val}_{today_str}.xlsx"

        st.download_button(
            label="📥 Download Final Excel File",
            data=buffer.getvalue(),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Please upload an Excel file to start.")
