import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Inventory Scanner App", layout="wide")
st.title("📦 Inventory Scanner with Camera")

# جلسة لتخزين البيانات
if "df" not in st.session_state:
    st.session_state.df = None
if "scanned" not in st.session_state:
    st.session_state.scanned = {}

# رفع ملف المنتجات
uploaded_file = st.file_uploader("📄 Upload Product File (Excel/CSV)", type=["xlsx", "xls", "csv"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # تأكد من الأعمدة
    if "Barcodes" in df.columns and "Available Quantity" in df.columns:
        df["Actual Quantity"] = 0
        st.session_state.df = df
    else:
        st.error("❌ File must contain 'Barcodes' and 'Available Quantity' columns.")

# لو الداتا موجودة
if st.session_state.df is not None:
    st.markdown("### 📷 Scan Product Barcode")
    
    # زر لتشغيل الكاميرا
    st.markdown(
        """
        <div id="reader" width="600px"></div>
        <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
        <script>
        function onScanSuccess(decodedText, decodedResult) {
            const barcodeInput = window.parent.document.querySelector('input[data-testid="stTextInput"]');
            if (barcodeInput) {
                barcodeInput.value = decodedText;
                const event = new Event('input', { bubbles: true });
                barcodeInput.dispatchEvent(event);
            }
        }

        const html5QrcodeScanner = new Html5QrcodeScanner(
            "reader", { fps: 10, qrbox: 250 }, false);
        html5QrcodeScanner.render(onScanSuccess);
        </script>
        """,
        unsafe_allow_html=True,
    )

    barcode = st.text_input("Or enter barcode manually:")

    if barcode:
        df = st.session_state.df
        # لو الباركود موجود في الجدول
        if barcode in df["Barcodes"].values:
            df.loc[df["Barcodes"] == barcode, "Actual Quantity"] += 1
            st.success(f"✅ Scanned: {barcode}")
        else:
            st.warning(f"⚠️ Barcode not found: {barcode}")
        st.session_state.df = df  # تحديث الجلسة

    # جدول النتيجة
    df = st.session_state.df
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
    st.dataframe(df, use_container_width=True)

    # تحميل إكسل
    @st.cache_data
    def to_excel(df):
        return df.to_excel(index=False, engine='xlsxwriter')

    st.download_button(
        "⬇️ Download Excel Report",
        to_excel(df),
        file_name=f"inventory_report_{datetime.datetime.now().date()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
