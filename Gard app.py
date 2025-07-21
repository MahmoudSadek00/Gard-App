import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# Step 1: Upload file
uploaded_file = st.file_uploader("Upload your inventory file", type=["csv", "xlsx"])

if uploaded_file and "df" not in st.session_state:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("⚠️ File must include 'Barcodes' and 'Available Quantity'")
            st.stop()

        df["Actual Quantity"] = 0
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

        st.session_state.df = df
        st.session_state.last_scanned = ""  # نستخدمه لمتابعة آخر باركود

        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

# Step 2: Handle scanning
if "df" in st.session_state:
    df = st.session_state.df
    st.subheader("📸 Scan Barcode")

    barcode = st.text_input("Scan or enter barcode manually", value="", key="scan_input")

    # لو الباركود اتغير عن آخر واحد اتسجل
    if barcode and barcode != st.session_state.get("last_scanned", ""):
        barcode = barcode.strip()
        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.success(f"✅ Barcode {barcode} counted.")
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

        st.session_state.df = df
        st.session_state.last_scanned = barcode  # نحفظ آخر باركود

        st.experimental_rerun()

    # عرض الجدول
    st.dataframe(df, use_container_width=True)

    # زر التحميل
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)

    st.download_button(
        label="📥 Download Updated File",
        data=buffer.getvalue(),
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
