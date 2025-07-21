import streamlit as st
import pandas as pd

st.set_page_config(page_title="Domanza Inventory App", layout="centered")
st.title("📦 Domanza Inventory Scanner")

# تحميل ملف الإكسل
uploaded_file = st.file_uploader("Upload Inventory File", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # عرض الجدول الأساسي
    st.markdown("### 🧾 Inventory Data")
    st.dataframe(df)

    # إدخال الباركود وزرارين confirm و clear
    st.markdown("### 📸 Scan Barcode")
    barcode_col, button_col, clear_col = st.columns([4, 1, 1])

    with barcode_col:
        st.text_input("Scan Barcode", key="barcode_input")

    with button_col:
        confirm_pressed = st.button("✔️ Confirm")

    with clear_col:
        clear_pressed = st.button("🧹 Clear")

    # استخراج القيمة اللي اتعمل لها سكان
    scanned_barcode = st.session_state.get("barcode_input", "").strip()

    # متغير مؤقت لعرض اسم المنتج
    product_name_display = ""

    if confirm_pressed and scanned_barcode:
        if scanned_barcode in df["Barcodes"].values:
            df.loc[df["Barcodes"] == scanned_barcode, "Available Quantity"] += 1

            matched = df.loc[df["Barcodes"] == scanned_barcode, "Product Name"]
            if not matched.empty:
                product_name_display = matched.values[0]
            else:
                product_name_display = "❌ Not Found"
        else:
            product_name_display = "❌ Not Found"

        # تصفير الباركود بعد التأكيد
        st.session_state["barcode_input"] = ""

    if clear_pressed:
        st.session_state["barcode_input"] = ""

    # عرض اسم المنتج إن وُجد
    st.markdown("### 🏷️ Product Name")
    st.text(product_name_display)

    # عرض الجدول بعد التحديث
    st.markdown("### ✅ Updated Inventory")
    st.dataframe(df)
