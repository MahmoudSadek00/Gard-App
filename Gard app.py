import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع الملف
uploaded_file = st.file_uploader("Upload your inventory file (Excel with multiple sheets)", type=["xlsx"])

if uploaded_file:
    # قراءة كل الشيتات في dict
    sheets_data = pd.read_excel(uploaded_file, sheet_name=None)

    # حفظ في session_state عند أول تحميل
    if "sheets_data" not in st.session_state:
        st.session_state.sheets_data = sheets_data
        # تجهيز df لكل شيت مع Actual Quantity و Difference
        for sheet_name, df in st.session_state.sheets_data.items():
            if 'Barcodes' not in df.columns or 'Available Quantity' not in df.columns:
                st.error(f"Sheet '{sheet_name}' must include 'Barcodes' and 'Available Quantity' columns")
                st.stop()
            df['Actual Quantity'] = 0
            # قد تكون Difference موجودة كـ formula في الأصل، لكن هنا نحافظ على نسخة محسوبة
            df['Difference'] = df['Actual Quantity'] - df['Available Quantity']
            st.session_state.sheets_data[sheet_name] = df

# اختيار البراند (اسم الشيت)
selected_brand = None
if "sheets_data" in st.session_state:
    sheet_names = list(st.session_state.sheets_data.keys())
    selected_brand = st.selectbox("Select Brand (Sheet)", sheet_names)

# خانة الباركود مع زر تشغيل الكاميرا (بدون كاميرا حاليًا)
if selected_brand:
    df = st.session_state.sheets_data[selected_brand]

    st.subheader(f"Brand: {selected_brand}")

    # خانة إدخال الباركود
    if "barcode_input" not in st.session_state:
        st.session_state.barcode_input = ""

    barcode = st.text_input("Scan or enter barcode", key="barcode_input")

    # Toggle camera placeholder button (تفعيل الكاميرا مستقبلاً)
    if st.button("Toggle Camera (Coming soon)"):
        st.info("Camera functionality will be added soon.")

    # معالجة سكان الباركود
    if barcode and len(barcode.strip()) > 0:
        barcode_val = barcode.strip()
        if barcode_val in df['Barcodes'].astype(str).values:
            df.loc[df['Barcodes'].astype(str) == barcode_val, 'Actual Quantity'] += 1
            df['Difference'] = df['Actual Quantity'] - df['Available Quantity']
            st.success(f"✅ Barcode '{barcode_val}' counted.")
            st.session_state.sheets_data[selected_brand] = df

            # اضبط علم المسح لمسح خانة الباركود وإعادة تشغيل آمنة
            st.session_state.clear_barcode_input = True

            st.experimental_rerun()
        else:
            st.warning(f"❌ Barcode '{barcode_val}' not found in brand '{selected_brand}'.")

# مسح خانة الباركود بأمان
if st.session_state.get("clear_barcode_input", False):
    st.session_state.barcode_input = ""
    st.session_state.clear_barcode_input = False

# عرض الجدول النهائي فقط للبراند المحدد
if selected_brand:
    st.dataframe(st.session_state.sheets_data[selected_brand], use_container_width=True)

    # زر تحميل الملف النهائي مجمع كل البراندات (جميع الشيتات في ملف واحد)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in st.session_state.sheets_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download Full Updated Inventory",
        data=output,
        file_name=f"inventory_updated_{pd.Timestamp.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
