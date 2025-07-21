import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# Step 1: Upload the file
uploaded_file = st.file_uploader("Upload your inventory file", type=["csv", "xlsx"])

if uploaded_file and "df" not in st.session_state:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Check required columns
        if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
            st.error("⚠️ File must include 'Barcodes' and 'Available Quantity'")
            st.stop()

        df["Actual Quantity"] = 0
        df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
        st.session_state.df = df
        st.session_state.last_barcode = ""  # to trigger rerun without direct edit to barcode_input

        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

# Step 2: Scan barcode
if "df" in st.session_state:
    df = st.session_state.df
    st.subheader("📸 Scan Barcode")

    # نصيحة: نخلي المستخدم يكتب الباركود وبعدين يدوس Enter (أو مسح تلقائي بعدين لو عايز)
    barcode = st.text_input("Scan or enter barcode", key="barcode_input")

    # فقط عالج لو الباركود اتغير فعليًا عن آخر واحد
    if barcode and barcode != st.session_state.get("last_barcode", ""):
        barcode = barcode.strip()

        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.success(f"✅ Barcode {barcode} counted.")
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

        st.session_state.df = df
        st.session_state.last_barcode = barcode  # سجل الباركود الحالي

        # إعادة تشغيل للتفريغ اليدوي
        st.experimental_rerun()

    st.dataframe(df, use_container_width=True)

    # Download button
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)

    st.download_button(
        label="📥 Download Updated File",
        data=buffer.getvalue(),
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
