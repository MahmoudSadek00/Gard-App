import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

# رفع الملف
uploaded_file = st.file_uploader("Upload your inventory file", type=["csv", "xlsx"])

# تحميل البيانات لأول مرة
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
        st.session_state.last_barcode = ""
        st.session_state.input_text = ""

        st.success("✅ File loaded successfully!")

    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

# التعامل مع السكان السريع
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

    # Reset الإدخال بعد كل سكان
    st.session_state.input_text = ""

# لو تم تحميل الملف
if "df" in st.session_state:
    st.subheader("📸 Scan Barcode")

    # هنا الإدخال بيترصد لوحده أي تغيير ويحرك الفانكشن
    st.text_input(
        "Scan barcode here",
        key="input_text",
        on_change=process_barcode,
        label_visibility="collapsed",
        placeholder="Waiting for barcode..."
    )

    # عرض الجدول
    st.dataframe(st.session_state.df, use_container_width=True)

    # تحميل الملف
    buffer = io.BytesIO()
    st.session_state.df.to_excel(buffer, index=False)

    st.download_button(
        label="📥 Download Updated File",
        data=buffer.getvalue(),
        file_name="updated_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
