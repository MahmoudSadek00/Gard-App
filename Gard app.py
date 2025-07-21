import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# Session state
if 'scanned_barcodes' not in st.session_state:
    st.session_state.scanned_barcodes = []

# File uploader
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names)
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()

    if "Barcodes" not in df.columns or "Available Quantity" not in df.columns or "Actual Quantity" not in df.columns:
        st.error("❌ Sheet must contain 'Barcodes', 'Available Quantity', and 'Actual Quantity' columns.")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    # تنظيف الباركود
    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)

    # سكان باركود
    st.markdown("### 📸 Scan Barcode")
    barcode_input = st.text_input("Scan Here", value="", label_visibility="collapsed")

    if barcode_input:
        barcode_input = barcode_input.strip()
        st.session_state.scanned_barcodes.append(barcode_input)
        st.text_input("Last Scanned", value=barcode_input, disabled=True)

    # تجهيز السكان
    scanned_df = pd.DataFrame(st.session_state.scanned_barcodes, columns=["Barcodes"])
    scanned_df["Barcodes"] = scanned_df["Barcodes"].astype(str).str.strip()
    scanned_df["Actual Quantity"] = 1
    scanned_df = scanned_df.groupby("Barcodes").sum().reset_index()

    # تحديث الشيت الأصلي مباشرة
    for _, row in scanned_df.iterrows():
        barcode = row["Barcodes"]
        count = row["Actual Quantity"]
        df.loc[df["Barcodes"] == barcode, "Actual Quantity"] = count

    # تحديث الفرق تلقائي
    if "Difference" in df.columns:
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    # عرض الشيت
    st.subheader("📋 Updated Sheet")
    st.dataframe(df)

    # تحميل
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df_to_csv(df)
    st.download_button("📥 Download Updated Sheet", data=csv, file_name="updated_inventory.csv", mime="text/csv")
