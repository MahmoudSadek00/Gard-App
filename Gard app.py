import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

uploaded_file = st.file_uploader("Upload your inventory file", type=["csv", "xlsx"])

if uploaded_file and "df" not in st.session_state:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("⚠️ File must include 'Barcodes' and 'Available Quantity' columns.")
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

    st.subheader("📸 Scan Barcode (Camera & Input)")

    html_code = """
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <div id="reader" style="width: 250px; margin: auto;"></div>
    <script>
    function sendBarcode(barcode) {
        const streamlitEvent = new CustomEvent("barcode_scanned", {detail: barcode});
        window.dispatchEvent(streamlitEvent);
    }

    let lastResult = null;
    const html5QrcodeScanner = new Html5QrcodeScanner(
        "reader", { fps: 10, qrbox: 200 });

    html5QrcodeScanner.render((decodedText, decodedResult) => {
        if (decodedText !== lastResult) {
            lastResult = decodedText;
            sendBarcode(decodedText);
        }
    });
    </script>
    """

    # استخدام st.query_params بدل st.experimental_get_query_params
    barcode = st.query_params.get("barcode", [""])[0]

    st.components.v1.html(html_code, height=280)

    manual_barcode = st.text_input("Or enter barcode manually")

    def add_barcode(bc):
        if bc in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == bc, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state.df = df
            st.success(f"✅ Barcode {bc} counted.")
        else:
            st.warning(f"❌ Barcode '{bc}' not found.")

    if barcode:
        add_barcode(barcode)
        st.experimental_set_query_params(barcode="")

    if manual_barcode:
        add_barcode(manual_barcode.strip())
        st.experimental_rerun()

    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Download Updated Inventory",
        data=buffer.getvalue(),
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
