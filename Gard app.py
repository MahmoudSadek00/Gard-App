import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

uploaded_file = st.file_uploader("Upload your inventory file", type=["xlsx", "xls"])

if uploaded_file:
    # قراءة كل الشيتات في الملف
    sheets_data = pd.read_excel(uploaded_file, sheet_name=None)

    # محاولة استخراج أسماء الفروع من أول شيت لو فيه عمود Branch
    first_sheet_df = next(iter(sheets_data.values()))
    if 'Branch' in first_sheet_df.columns:
        branches = first_sheet_df['Branch'].dropna().unique().tolist()
        # لو لقى فرع واحد فقط، نخليه هو الافتراضي والوحيد
        if len(branches) == 1:
            selected_branch = branches[0]
            # اختار الشيت اللي اسمه الفرع دا لو موجود، أو خلي اول شيت
            if selected_branch in sheets_data:
                selected_df = sheets_data[selected_branch]
            else:
                selected_df = first_sheet_df
        else:
            selected_branch = st.selectbox("Select Branch / Brand", branches)
            selected_df = sheets_data.get(selected_branch, first_sheet_df)
    else:
        # لو مفيش عمود Branch، ندي اختيار براند من أسماء الشيتات
        sheet_names = list(sheets_data.keys())
        selected_branch = st.selectbox("Select Branch / Brand (sheet)", sheet_names)
        selected_df = sheets_data[selected_branch]

    # عرض بيانات الشيت المحدد
    st.write(f"Showing data for: **{selected_branch}**")
    st.dataframe(selected_df)

    # تأكد من وجود الأعمدة المهمة
    required_cols = ['Barcodes', 'Available Quantity']
    missing_cols = [col for col in required_cols if col not in selected_df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
    else:
        if 'Actual Quantity' not in selected_df.columns:
            selected_df['Actual Quantity'] = 0
        if 'Difference' not in selected_df.columns:
            selected_df['Difference'] = selected_df['Actual Quantity'] - selected_df['Available Quantity']

        # خانة إدخال الباركود
        barcode_input = st.text_input("Scan or enter barcode:")

        if barcode_input:
            barcode = barcode_input.strip()
            if barcode in selected_df['Barcodes'].astype(str).values:
                selected_df.loc[selected_df['Barcodes'].astype(str) == barcode, 'Actual Quantity'] += 1
                selected_df['Difference'] = selected_df['Actual Quantity'] - selected_df['Available Quantity']
                st.success(f"Barcode {barcode} counted.")
                # امسح الخانة بعد الإدخال (تحديث الصفحة)
                st.experimental_rerun()
            else:
                st.warning(f"Barcode '{barcode}' not found.")

        # عرض الجدول المحدث
        st.dataframe(selected_df)

        # تنزيل الملف المحدث مع اسم من الفرع والتاريخ
        buffer = io.BytesIO()
        today_str = datetime.today().strftime("%Y-%m-%d")
        file_name = f"{selected_branch}_{today_str}.xlsx"

        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            selected_df.to_excel(writer, index=False, sheet_name=selected_branch)

        st.download_button(
            label="📥 Download Updated Inventory",
            data=buffer.getvalue(),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
