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

    st.subheader("📸 Scan or Enter Barcode")

    # HTML + JS for barcode scanner (small box)
    html_code = """
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <div id="reader" style="width: 200px; margin: auto;"></div>
    <script>
    const sendBarcodeToStreamlit = (barcode) => {
        const inputField = window.parent.document.querySelector('input[aria-label="Barcode Input"]');
        if(inputField){
            inputField.value = barcode;
            inputField.dispatchEvent(new Event('input', { bubbles: true }));
        }
    };

    let lastResult = null;
    const html5QrcodeScanner = new Html5QrcodeScanner(
        "reader", { fps: 10, qrbox: 200 });

    html5QrcodeScanner.render((decodedText, decodedResult) => {
        if (decodedText !== lastResult) {
            lastResult = decodedText;
            sendBarcodeToStreamlit(decodedText);
        }
    });
    </script>
    """

    # unified barcode input field
    barcode = st.text_input("Barcode Input", key="barcode_input")

    def add_barcode(bc):
        if bc in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == bc, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state.df = df
            st.success(f"✅ Barcode {bc} counted.")
        else:
            st.warning(f"❌ Barcode '{bc}' not found.")

    # Trigger count when barcode changes and is non-empty
    if barcode and barcode.strip():
        add_barcode(barcode.strip())
        # Clear the input after processing to allow scanning next barcode
        st.session_state.barcode_input = ""

    st.components.v1.html(html_code, height=260)

    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button(
        label="📥 Download Updated Inventory",
        data=buffer.getvalue(),
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
