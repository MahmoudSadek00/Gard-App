import streamlit as st
import pandas as pd
from datetime import datetime
import io

# HTML + JS لمسح باركود بالكاميرا (html5-qrcode) بحجم صغير تحت خانة الباركود
CAMERA_HTML = """
<div style="width: 300px; margin-bottom: 10px;" id="reader"></div>
<script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
<script>
function onScanSuccess(decodedText, decodedResult) {
  window.parent.postMessage({type: 'barcode', code: decodedText}, '*');
  html5QrcodeScanner.clear();
}
var html5QrcodeScanner = new Html5QrcodeScanner(
  "reader", { fps: 10, qrbox: 250, aspectRatio: 1.2, facingMode: "environment" }, false);
html5QrcodeScanner.render(onScanSuccess);
</script>
"""

st.set_page_config(page_title="📦 Inventory Scanner with Camera", layout="wide")
st.title("📦 Inventory Scanner App with Camera")

uploaded_file = st.file_uploader("Upload your inventory file", type=["xlsx", "xls"])

if uploaded_file:
    sheets_data = pd.read_excel(uploaded_file, sheet_name=None)

    # محاولة الحصول على فروع (Branch) من أول شيت
    first_sheet_df = next(iter(sheets_data.values()))
    if 'Branch' in first_sheet_df.columns:
        branches = first_sheet_df['Branch'].dropna().unique().tolist()
        selected_branch = st.selectbox("Select Branch / Brand", branches)
        # حاول تجيب الشيت بنفس اسم الفرع، لو مش موجود خد اول شيت
        selected_df = sheets_data.get(selected_branch, first_sheet_df)
    else:
        # لو مفيش عمود Branch ندي اختيار من أسماء الشيتات
        sheet_names = list(sheets_data.keys())
        selected_branch = st.selectbox("Select Branch / Brand (sheet)", sheet_names)
        selected_df = sheets_data[selected_branch]

    # تأكد من الأعمدة المطلوبة
    required_cols = ['Barcodes', 'Available Quantity']
    missing_cols = [col for col in required_cols if col not in selected_df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.stop()

    if 'Actual Quantity' not in selected_df.columns:
        selected_df['Actual Quantity'] = 0
    if 'Difference' not in selected_df.columns:
        selected_df['Difference'] = selected_df['Actual Quantity'] - selected_df['Available Quantity']

    st.subheader("Scan or enter barcode")

    # عرض خانة باركود
    barcode_input = st.text_input("Enter or scan barcode", key="barcode_input")

    # زر تفعيل الكاميرا مع عرض مدمج تحت الخانة
    if st.button("Toggle Camera Scanner"):
        st.session_state.show_camera = not st.session_state.get("show_camera", False)
    else:
        if "show_camera" not in st.session_state:
            st.session_state.show_camera = False

    if st.session_state.show_camera:
        st.components.v1.html(CAMERA_HTML, height=320, scrolling=False)

    # استقبال باركود من الكاميرا (JS) عبر الرسائل
    barcode_js = st.experimental_get_query_params().get("barcode", [""])[0]
    # لو في باركود من الكاميرا حدث خانة الإدخال تلقائياً
    if barcode_js and barcode_js != barcode_input:
        barcode_input = barcode_js

    # معالجة إدخال الباركود (كتابة أو من الكاميرا)
    if barcode_input:
        barcode = barcode_input.strip()
        if barcode in selected_df['Barcodes'].astype(str).values:
            selected_df.loc[selected_df['Barcodes'].astype(str) == barcode, 'Actual Quantity'] += 1
            selected_df['Difference'] = selected_df['Actual Quantity'] - selected_df['Available Quantity']
            st.success(f"✅ Barcode {barcode} counted.")
            # تفريغ الخانة بعد الإدخال
            st.session_state.barcode_input = ""
            st.experimental_rerun()
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

    st.dataframe(selected_df)

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
