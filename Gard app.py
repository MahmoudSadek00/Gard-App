import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Initial session states
if 'barcode_counts' not in st.session_state:
    st.session_state.barcode_counts = {}
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ""
if 'df' not in st.session_state:
    st.session_state.df = None

# Upload Excel File
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file and st.session_state.df is None:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names)
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()

    required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ Sheet must contain these columns: {required_columns}")
        st.stop()

    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)

    st.session_state.df = df.copy()

if st.session_state.df is not None:
    df = st.session_state.df

    # ======== Barcode Camera Scanner ========
    st.markdown("### 📸 Camera Barcode Scanner")
    html("""
    <script src="https://unpkg.com/html5-qrcode"></script>
    <div id="reader" width="600px"></div>
    <script>
    function onScanSuccess(decodedText, decodedResult) {
        const streamlitInput = window.parent.document.querySelector('input[data-testid="stTextInput"]');
        if (streamlitInput) {
            streamlitInput.value = decodedText;
            streamlitInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    let html5QrcodeScanner = new Html5QrcodeScanner(
        "reader", { fps: 10, qrbox: 250 });
    html5QrcodeScanner.render(onScanSuccess);
    </script>
    """, height=400)

    # ======== Manual Input (Updated by Camera) ========
    scanned = st.text_input("Or Enter Barcode Manually", value=st.session_state.barcode_input)

    product_name_display = ""

    if scanned:
        scanned = scanned.strip()

        # Count & update
        if scanned in st.session_state.barcode_counts:
            st.session_state.barcode_counts[scanned] += 1
        else:
            st.session_state.barcode_counts[scanned] = 1

        # Update Actual Quantity
        if scanned in df["Barcodes"].values:
            count = st.session_state.barcode_counts[scanned]
            df.loc[df["Barcodes"] == scanned, "Actual Quantity"] = count
            product_name_display = df.loc[df["Barcodes"] == scanned, "Product Name"].values[0]
        else:
            product_name_display = "❌ Not Found"

        st.session_state.df = df
        st.session_state.barcode_input = ""  # Clear input
    else:
        st.session_state.barcode_input = scanned

    # Display product name
    st.markdown("#### 🏷️ Product Name")
    st.markdown(f"""
        <div style="padding: 0.75rem 1rem; background-color: #e6f4ea; border: 2px solid #2e7d32;
                    border-radius: 5px; font-weight: bold; font-size: 16px;">
            {product_name_display}
        </div>
    """, unsafe_allow_html=True)

    # Calculate difference
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    # Show table
    st.subheader("📋 Updated Sheet")
    st.dataframe(df)

    # Scanned barcodes log
    st.markdown("### ✅ Scanned Barcode Log")
    st.write(pd.DataFrame([
        {"Barcode": k, "Scanned Count": v}
        for k, v in st.session_state.barcode_counts.items()
    ]))

    # Download CSV
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(df)
    st.download_button("📥 Download Updated Sheet", data=csv, file_name="updated_inventory.csv", mime="text/csv")
