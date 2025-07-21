import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner with Camera")

# رفع الملف
uploaded_file = st.file_uploader("Upload your inventory file", type=["csv", "xlsx"])

if uploaded_file and "df" not in st.session_state:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # تحقق من الأعمدة المطلوبة
        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("⚠️ File must include 'Barcodes' and 'Available Quantity'")
            st.stop()

        df["Actual Quantity"] = 0
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
        st.session_state.df = df

        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

if "df" in st.session_state:
    df = st.session_state.df

    st.subheader("📸 Barcode Scanner")

    # زر تشغيل/ايقاف الكاميرا
    if 'camera_on' not in st.session_state:
        st.session_state.camera_on = False

    toggle = st.button("▶️ Start/Stop Camera")
    if toggle:
        st.session_state.camera_on = not st.session_state.camera_on

    # خانة الإدخال للباركود (كتابة أو من الكاميرا)
    barcode_val = st.text_input("Scan or enter barcode here", key="barcode_input", label_visibility="visible")

    if barcode_val:
        barcode_val = barcode_val.strip()
        if barcode_val in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode_val, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state.df = df
            st.success(f"✅ Barcode '{barcode_val}' counted.")
            # تفريغ خانة الإدخال
            st.session_state.barcode_input = ""
        else:
            st.warning(f"❌ Barcode '{barcode_val}' not found.")
            st.session_state.barcode_input = ""

    # عرض مربع الكاميرا مع تصميم
    if st.session_state.camera_on:
        camera_html = """
        <div style="width: 250px; height: 250px; border: 3px solid #4CAF50; border-radius: 12px; margin-bottom:10px;">
            <div id="reader" style="width: 100%; height: 100%;"></div>
        </div>

        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
        <script>
        function onScanSuccess(decodedText, decodedResult) {
            // ارسل الباركود لـ Streamlit
            const input = window.parent.document.querySelector('input[data-key="barcode_input"]');
            if (input) {
                input.value = decodedText;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
        function onScanFailure(error) {
            // لا تفعل شيئاً عند فشل المسح
        }
        let html5QrcodeScanner = new Html5QrcodeScanner(
            "reader", { fps: 10, qrbox: 250 });
        html5QrcodeScanner.render(onScanSuccess, onScanFailure);
        </script>
        """
        st.components.v1.html(camera_html, height=280)

    # عرض الجدول
    st.subheader("📝 Inventory Table")
    st.dataframe(df, use_container_width=True)

    # زر تحميل الملف المعدل
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Download Updated Inventory",
        data=buffer.getvalue(),
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
