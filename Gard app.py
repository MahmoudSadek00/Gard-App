import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

uploaded_file = st.file_uploader("Upload your Excel inventory file", type=["xlsx"])

if uploaded_file:
    sheets = pd.read_excel(uploaded_file, sheet_name=None)
    st.session_state["sheets_data"] = sheets
    brand_list = list(sheets.keys())
else:
    brand_list = []

if brand_list:
    selected_brand = st.selectbox("Select Brand", brand_list)
    df = st.session_state["sheets_data"][selected_brand]

    for col in ["Barcodes", "Available Quantity"]:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            st.stop()

    if "Actual Quantity" not in df.columns:
        df["Actual Quantity"] = 0
    if "Difference" not in df.columns:
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

    barcode = st.text_input("Scan or enter barcode", key="barcode_input")

    # تابع معالجة الباركود
    def process_barcode(barcode_value):
        barcode_value = barcode_value.strip()
        if len(barcode_value) >= 9:
            mask = df["Barcodes"].astype(str) == barcode_value
            if mask.any():
                df.loc[mask, "Actual Quantity"] += 1
                df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
                st.success(f"Barcode {barcode_value} counted.")
            else:
                st.warning(f"Barcode {barcode_value} not found.")
            return True
        return False

    # لو خانة الباركود فيها قيمة (يعني ضغط Enter أو خرج من الخانة)
    if barcode:
        if process_barcode(barcode):
            # بعد المعالجة نفرغ الخانة من غير زرار
            st.session_state["barcode_input"] = ""

    st.dataframe(df, use_container_width=True)

    buffer = io.BytesIO()
    today_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"{selected_brand}_{today_str}_inventory.xlsx"
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for brand_name, brand_df in st.session_state["sheets_data"].items():
            if brand_name == selected_brand:
                brand_df = df
            else:
                if "Actual Quantity" not in brand_df.columns:
                    brand_df["Actual Quantity"] = 0
                if "Difference" not in brand_df.columns:
                    brand_df["Difference"] = brand_df["Actual Quantity"] - brand_df["Available Quantity"]
            brand_df.to_excel(writer, sheet_name=brand_name, index=False)

    st.download_button(
        label="Download Updated Inventory",
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
