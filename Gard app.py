import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

uploaded_file = st.file_uploader("Upload your inventory file (with multiple sheets)", type=["xlsx", "xls"])

# تحميل الملف بالكامل كـ dict من الشيتات
if uploaded_file and "sheets_data" not in st.session_state:
    try:
        all_sheets = pd.read_excel(uploaded_file, sheet_name=None)

        st.session_state.sheets_data = all_sheets
        st.session_state.selected_sheet = None
        st.session_state.df = None
        st.session_state.input_text = ""
        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        st.stop()

# لو تم تحميل البيانات، خلي المستخدم يختار التاب
if "sheets_data" in st.session_state:
    sheet_names = list(st.session_state.sheets_data.keys())

    selected_tab = st.selectbox("🗂️ Select Brand Sheet", sheet_names)

    if selected_tab != st.session_state.selected_sheet:
        df = st.session_state.sheets_data[selected_tab].copy()

        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("⚠️ Selected sheet must include 'Barcodes' and 'Available Quantity'")
            st.stop()

        df["Actual Quantity"] = 0
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

        st.session_state.df = df
        st.session_state.selected_sheet = selected_tab

# معالجة الباركود
def process_barcode():
    barcode = st.session_state.input_text.strip()
    df = st.session_state.df

    if barcode:
        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.session_state.df = df
            st.success(f"✅ Barcode {barcode} counted.")
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

    st.session_state.input_text = ""

# لو تم اختيار تاب
if st.session_state.get("df") is not None:
    st.subheader("📸 Scan Barcode")

    st.text_input(
        "Scan barcode here",
        key="input_text",
        on_change=process_barcode,
        label_visibility="collapsed",
        placeholder="Waiting for barcode..."
    )

    st.dataframe(st.session_state.df, use_container_width=True)

    # تحميل الملف
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet_name, sheet_df in st.session_state.sheets_data.items():
            if sheet_name == st.session_state.selected_sheet:
                st.session_state.df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)

    st.download_button(
        label="📥 Download Updated File",
        data=buffer.getvalue(),
        file_name="updated_inventory_with_changes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
