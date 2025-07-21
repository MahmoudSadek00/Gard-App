import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

uploaded_file = st.file_uploader("Upload your inventory file", type=["csv", "xlsx"])

if uploaded_file and "sheets_data" not in st.session_state:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheets_data = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
            st.session_state.sheets_data = sheets_data

        # Validate all sheets
        for sheet_name, sheet_df in st.session_state.sheets_data.items():
            if not {"Barcodes", "Available Quantity"}.issubset(sheet_df.columns):
                st.error(f"Sheet '{sheet_name}' is missing required columns 'Barcodes' or 'Available Quantity'.")
                st.stop()

        for sheet_name in st.session_state.sheets_data:
            st.session_state.sheets_data[sheet_name]["Actual Quantity"] = 0

        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

if "sheets_data" in st.session_state:
    sheets_data = st.session_state.sheets_data
    st.subheader("📸 Scan or Enter Barcode")

    barcode_input = st.text_input("Scan or type barcode:", key="barcode_input")

    # كاميرا + زر تشغيل/ايقاف مع تحسين التصميم
    camera_html = """
    <style>
      #reader {
        width: 250px; 
        height: 200px; 
        border: 2px solid #4CAF50;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 10px;
      }
      #camera-toggle {
        cursor: pointer;
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 8px 16px;
        font-size: 16px;
        border-radius: 25px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      #camera-toggle svg {
        fill: white;
        width: 20px;
        height: 20px;
      }
    </style>
    <button id="camera-toggle" onclick="toggleCamera()">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 5c-3.86 0-7 3.14-7 7s3.14 7 7 7 7-3.14 7-7-3.14-7-7-7zm0 12.93c-3.26 0-5.93-2.67-5.93-5.93S8.74 6.07 12 6.07 17.93 8.74 17.93 12 15.26 17.93 12 17.93zm-1-5.93V8h2v4h-2zm0 4v-2h2v2h-2z"/></svg>
      Toggle Camera
    </button>
    <div id="reader" style="display:none"></div>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script>
    let scanner = null;
    let cameraOn = false;
    function toggleCamera(){
        const reader = document.getElementById("reader");
        const btn = document.getElementById("camera-toggle");
        if(cameraOn){
            scanner.clear().then(() => {
                reader.style.display = "none";
                btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 5c-3.86 0-7 3.14-7 7s3.14 7 7 7 7-3.14 7-7-3.14-7-7-7zm0 12.93c-3.26 0-5.93-2.67-5.93-5.93S8.74 6.07 12 6.07 17.93 8.74 17.93 12 15.26 17.93 12 17.93zm-1-5.93V8h2v4h-2zm0 4v-2h2v2h-2z"/></svg> Toggle Camera`;
                cameraOn = false;
            }).catch(err => console.error(err));
        } else {
            reader.style.display = "block";
            scanner = new Html5Qrcode("reader");
            scanner.start({ facingMode: { exact: "environment" } }, { fps: 10, qrbox: 250 },
                (decodedText, decodedResult) => {
                    const input = window.parent.document.querySelector('input[data-key="barcode_input"]');
                    if(input){
                        input.value = decodedText;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                },
                (errorMessage) => {
                    // ignore errors
                }
            ).catch(err => console.error(err));
            btn.innerHTML = `&#10060; Stop Camera`;
            cameraOn = true;
        }
    }
    </script>
    """
    st.components.v1.html(camera_html, height=300)

    # Process barcode input
    if barcode_input:
        barcode = barcode_input.strip()
        found = False
        for sheet_name, sheet_df in sheets_data.items():
            if barcode in sheet_df["Barcodes"].astype(str).values:
                idxs = sheet_df.index[sheet_df["Barcodes"].astype(str) == barcode].tolist()
                for idx in idxs:
                    sheets_data[sheet_name].at[idx, "Actual Quantity"] += 1
                found = True
        if found:
            st.success(f"✅ Barcode '{barcode}' counted.")
            st.session_state["barcode_input"] = ""
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

    # Show sheets with updated quantities
    for sheet_name, sheet_df in sheets_data.items():
        sheet_df["Difference"] = sheet_df["Actual Quantity"] - sheet_df["Available Quantity"]
        st.subheader(f"Sheet: {sheet_name}")
        st.dataframe(sheet_df, use_container_width=True)

    # Download updated sheets
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
