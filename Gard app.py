import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Inventory Scanner with html5-qrcode", layout="wide")
st.title("📦 Inventory Scanner with Camera (html5-qrcode)")

uploaded_file = st.file_uploader("Upload your inventory file (Excel or CSV)", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    if not {"Barcodes", "Available Quantity"}.issubset(df.columns):
        st.error("File must contain 'Barcodes' and 'Available Quantity' columns.")
        st.stop()

    if "Actual Quantity" not in df.columns:
        df["Actual Quantity"] = 0

    if "Difference" not in df.columns:
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    if "df" not in st.session_state:
        st.session_state.df = df

    df = st.session_state.df
    scanned_barcode = st.empty()

    html_code = """
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <div id="reader" style="width: 400px;"></div>
    <script>
    function sendBarcode(barcode) {
        const streamlitEvent = new CustomEvent("barcode_scanned", {detail: barcode});
        window.dispatchEvent(streamlitEvent);
    }

    let lastResult = null;
    const html5QrcodeScanner = new Html5QrcodeScanner(
        "reader", { fps: 10, qrbox: 250 });

    html5QrcodeScanner.render((decodedText, decodedResult) => {
        if (decodedText !== lastResult) {
            lastResult = decodedText;
            sendBarcode(decodedText);
        }
    });
    </script>
    """

    barcode = st.query_params.get("barcode", [None])[0]

    st.components.v1.html(html_code, height=450)

    manual_barcode = st.text_input("Or enter barcode manually:")

    final_barcode = None
    if manual_barcode and manual_barcode.strip():
        final_barcode = manual_barcode.strip()
    elif barcode:
        final_barcode = barcode.strip()

    if final_barcode:
        if final_barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == final_barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state.df = df
            scanned_barcode.success(f"Barcode {final_barcode} counted!")
        else:
            scanned_barcode.warning(f"Barcode {final_barcode} not found in inventory.")

    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Download updated inventory",
        data=buffer.getvalue(),
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.info("Please upload an inventory file to start scanning.")
