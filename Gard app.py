import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Inventory Scanner", layout="wide")

# Initialize session states
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "sheets" not in st.session_state:
    st.session_state.sheets = []
if "df_dict" not in st.session_state:
    st.session_state.df_dict = {}
if "barcode_input" not in st.session_state:
    st.session_state.barcode_input = ""
if "selected_sheet" not in st.session_state:
    st.session_state.selected_sheet = None

# File upload
if not st.session_state.uploaded:
    file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])
    if file:
        xls = pd.ExcelFile(file)
        st.session_state.sheets = xls.sheet_names
        st.session_state.df_dict = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
        st.session_state.uploaded = True
        st.rerun()

# Sheet selection
if st.session_state.uploaded and st.session_state.sheets:
    st.session_state.selected_sheet = st.selectbox("Select Brand Sheet", st.session_state.sheets)

    if st.session_state.selected_sheet:
        df = st.session_state.df_dict[st.session_state.selected_sheet]

        # Ensure required columns exist
        if 'Barcodes' not in df.columns or 'Actual Quantity' not in df.columns:
            st.error("Sheet must contain 'Barcodes' and 'Actual Quantity' columns.")
            st.stop()

        # Barcode input
        barcode = st.text_input("Scan or Enter Barcode", value=st.session_state.barcode_input, key="barcode_field")

        # Process barcode
        if barcode:
            barcode = barcode.strip()
            matches = df[df["Barcodes"] == barcode].index.tolist()

            if matches:
                idx = matches[0]
                current_value = df.at[idx, "Actual Quantity"]
                df.at[idx, "Actual Quantity"] = current_value + 1 if pd.notna(current_value) else 1
                st.success(f"✅ Updated quantity for barcode: {barcode}")
            else:
                st.warning(f"❌ Barcode {barcode} not found in selected sheet.")

            st.session_state.barcode_input = ""  # Clear input
            st.rerun()

        # Show updated dataframe
        st.dataframe(df)

        # Download button
        if st.button("Download Updated Sheet"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for sheet_name, sheet_df in st.session_state.df_dict.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name="updated_inventory.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
