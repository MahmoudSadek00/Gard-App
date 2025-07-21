import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# Initialize session state
if 'actual_quantities' not in st.session_state:
    st.session_state.actual_quantities = {}
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ""

# File uploader
uploaded_file = st.file_uploader("Upload Excel Inventory File", type=["xlsx"])
if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet_name = st.selectbox("Select Brand Sheet", sheet_names)

    if sheet_name:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Ensure required columns exist
        if "Barcode" not in df.columns or "Available Quantity" not in df.columns:
            st.error("Sheet must contain 'Barcode' and 'Available Quantity' columns.")
            st.stop()

        df["Actual Quantity"] = df["Barcode"].map(st.session_state.actual_quantities).fillna(0).astype(int)
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

        col1, col2 = st.columns([3, 1])
        with col1:
            barcode = st.text_input("Scan Barcode", value=st.session_state.barcode_input, key="barcode_input_box")
        with col2:
            if st.button("Submit"):
                if barcode:
                    st.session_state.actual_quantities[barcode] = st.session_state.actual_quantities.get(barcode, 0) + 1
                    st.session_state.barcode_input = ""  # clear barcode input
                    st.experimental_rerun()

        st.dataframe(df, use_container_width=True)

        # Optional download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Updated')
        st.download_button("Download Updated Sheet", data=output.getvalue(), file_name="updated_inventory.xlsx")
