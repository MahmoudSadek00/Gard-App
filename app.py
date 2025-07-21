import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Inventory Camera App", layout="wide")
st.title("📦 Inventory Scanner with Camera")

# Step 1: Upload products file
products_file = st.file_uploader("Upload Products File (CSV or Excel with 'Barcodes' & 'Available Quantity')", type=['csv', 'xlsx'])

if products_file:
    if products_file.name.endswith('.csv'):
        df = pd.read_csv(products_file)
    else:
        df = pd.read_excel(products_file)

    # Ensure required columns exist
    if 'Barcodes' not in df.columns or 'Available Quantity' not in df.columns:
        st.error("File must contain 'Barcodes' and 'Available Quantity' columns.")
    else:
        df['Actual Quantity'] = 0

        st.markdown("## Scan Barcodes")

        # HTML + JS barcode scanner using html5-qrcode
        components.html("""
            <div>
                <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
                <div id="reader" width="600px"></div>
                <script>
                    function onScanSuccess(decodedText, decodedResult) {
                        const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
                        input.value = decodedText;
                        const event = new Event('input', { bubbles: true });
                        input.dispatchEvent(event);
                    }
                    const html5QrCode = new Html5Qrcode("reader");
                    html5QrCode.start(
                        { facingMode: "environment" },
                        { fps: 10, qrbox: 250 },
                        onScanSuccess);
                </script>
            </div>
        """, height=300)

        # Hidden input to receive scanned barcode
        scanned_barcode = st.text_input("Scanned Barcode (auto-filled)")

        if scanned_barcode:
            if scanned_barcode in df['Barcodes'].values:
                df.loc[df['Barcodes'] == scanned_barcode, 'Actual Quantity'] += 1
                st.success(f"✅ Counted 1 more for barcode: {scanned_barcode}")
            else:
                st.warning(f"❌ Barcode not found: {scanned_barcode}")

        # Compute difference
        df['Difference'] = df['Actual Quantity'] - df['Available Quantity']

        st.markdown("## Final Inventory Table")
        st.dataframe(df)

        # Export
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(df)
        st.download_button(
            "📥 Download Final CSV",
            csv,
            "final_inventory.csv",
            "text/csv",
            key='download-csv'
        )
