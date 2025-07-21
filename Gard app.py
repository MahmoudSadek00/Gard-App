import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Inventory Scanner with Camera", layout="wide")
st.title("📦 Inventory Scanner with Camera (HTML5 QR Code)")

# رفع ملف الإكسل أو CSV
uploaded_file = st.file_uploader("Upload your inventory file (Excel or CSV)", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # تحقق من الأعمدة المطلوبة
    required_cols = ['Barcodes', 'Available Quantity']
    if not all(col in df.columns for col in required_cols):
        st.error(f"File must contain these columns: {required_cols}")
        st.stop()

    # اضف عمود Actual Quantity إذا مش موجود
    if 'Actual Quantity' not in df.columns:
        df['Actual Quantity'] = 0
    if 'Difference' not in df.columns:
        df['Difference'] = df['Actual Quantity'] - df['Available Quantity']

    # خزن الداتا في session_state
    st.session_state.df = df

    # عنصر html لقراءة الباركود باستخدام كاميرا الموبايل
    barcode_html = """
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <div style="width: 100%; max-width: 500px;" id="reader"></div>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // إرسال القيمة للستريمليت عبر تحديث عنوان الصفحة (URL)
            window.parent.postMessage({barcode: decodedText}, "*");
            // لإيقاف المسح مؤقتاً
            html5QrcodeScanner.clear();
        }
        var html5QrcodeScanner = new Html5QrcodeScanner(
            "reader", { fps: 10, qrbox: 250 }, /* verbose= */ false);
        html5QrcodeScanner.render(onScanSuccess);
    </script>
    """

    # نعرض ال html داخل Streamlit
    st.components.v1.html(barcode_html, height=400)

    # استقبال الباركود المرسل من الـ JS
    from streamlit_javascript import st_javascript
    scanned_code = st_javascript("window.addEventListener('message', event => { if(event.data.barcode) { window.streamlit.setComponentValue(event.data.barcode); } });")

    if scanned_code:
        # كل مرة يتم سكان يتضاف لل Actual Quantity
        df = st.session_state.df
        barcode = scanned_code.strip()
        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state.df = df
            st.success(f"Barcode {barcode} counted!")
        else:
            st.warning(f"Barcode {barcode} not found in inventory.")

    # عرض الجدول المحدث
    st.dataframe(st.session_state.df)

    # زر تحميل الملف النهائي
    buffer = io.BytesIO()
    st.session_state.df.to_excel(buffer, index=False)
    st.download_button("Download updated inventory", buffer.getvalue(), "updated_inventory.xlsx")

else:
    st.info("Please upload your inventory file to start scanning.")

