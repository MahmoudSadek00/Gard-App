import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# Step 1: Upload file
uploaded_file = st.file_uploader("Upload your inventory file", type=["csv", "xlsx"])

if uploaded_file and "sheets_data" not in st.session_state:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            xls = pd.ExcelFile(uploaded_file)
            # Load all sheets into dict
            sheets_data = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
            st.session_state.sheets_data = sheets_data
            # Flatten first sheet for barcode base (you can choose any sheet)
            df = sheets_data[xls.sheet_names[0]]

        # Validate columns exist in at least one sheet
        for sheet_name, sheet_df in st.session_state.sheets_data.items():
            if not {"Barcodes", "Available Quantity"}.issubset(sheet_df.columns):
                st.error(f"Sheet '{sheet_name}' is missing required columns 'Barcodes' or 'Available Quantity'.")
                st.stop()

        # Initialize Actual Quantity for all sheets
        for sheet_name in st.session_state.sheets_data:
            st.session_state.sheets_data[sheet_name]["Actual Quantity"] = 0

        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

# Barcode input and camera scan combined
if "sheets_data" in st.session_state:
    sheets_data = st.session_state.sheets_data

    st.subheader("📸 Scan or Enter Barcode")

    # Barcode input text box
    barcode_input = st.text_input("Scan or type barcode:", key="barcode_input")

    # Camera scan component with html5-qrcode to detect back camera:
    camera_html = """
    <div id="reader" style="width: 300px; height: 200px;"></div>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script>
    function onScanSuccess(decodedText, decodedResult) {
        const input = window.parent.document.querySelector('input[data-key="barcode_input"]');
        if (input) {
            input.value = decodedText;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    function onScanFailure(error) {
        // ignore scan failure, could log if needed
    }
    let config = {
      fps: 10,
      qrbox: 250,
      facingMode: { exact: "environment" }  // back camera
    };
    let html5QrcodeScanner = new Html5QrcodeScanner("reader", config);
    html5QrcodeScanner.render(onScanSuccess, onScanFailure);
    </script>
    """
    st.components.v1.html(camera_html, height=250)

    # Process barcode input
    if barcode_input:
        barcode = barcode_input.strip()
        found = False
        for sheet_name, sheet_df in sheets_data.items():
            # Convert barcodes column to string for comparison
            if barcode in sheet_df["Barcodes"].astype(str).values:
                idxs = sheet_df.index[sheet_df["Barcodes"].astype(str) == barcode].tolist()
                for idx in idxs:
                    sheets_data[sheet_name].at[idx, "Actual Quantity"] += 1
                found = True
        if found:
            st.success(f"✅ Barcode '{barcode}' counted.")
            # Clear input box after processing using session state trick
            st.session_state["barcode_input"] = ""
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

    # Show all sheets data with updated Actual Quantity and Difference
    for sheet_name, sheet_df in sheets_data.items():
        sheet_df["Difference"] = sheet_df["Actual Quantity"] - sheet_df["Available Quantity"]
        st.subheader(f"Sheet: {sheet_name}")
        st.dataframe(sheet_df, use_container_width=True)

    # Download all sheets as Excel with updated quantities
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        for sheet_name, sheet_df in sheets_data.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Updated Inventory Excel",
        data=buffer,
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
