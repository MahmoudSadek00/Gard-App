import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Domanza Inventory App with Camera")

# File uploader
uploaded_file = st.file_uploader("Upload Inventory Excel File", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.selectbox("Select Brand Sheet", sheet_names)
    df = all_sheets[selected_sheet]
    df.columns = df.columns.str.strip()

    required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ Sheet must contain these columns: {required_columns}")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    # تنظيف الباركود
    df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
    df["Actual Quantity"] = df["Actual Quantity"].fillna(0).astype(int)

    # سكان باركود
    st.markdown("### 📸 Scan Barcode")

    cols = st.columns([2, 2])  # خليتين جنب بعض: واحدة للباركود، والتانية لاسم المنتج

    with cols[0]:
        barcode_input = st.text_input("Scan Here", value="", label_visibility="visible")

    product_name_display = ""

    if barcode_input:
        barcode_input = barcode_input.strip()

        # جلب اسم المنتج
        matched_product = df.loc[df["Barcodes"] == barcode_input, "Product Name"]
        if not matched_product.empty:
            product_name_display = matched_product.iloc[0]
        else:
            product_name_display = "❌ Not Found"

        # تحديث الكمية
        df.loc[df["Barcodes"] == barcode_input, "Actual Quantity"] = 1

    with cols[1]:
        st.text_input("🧾 Product Name", value=product_name_display, disabled=True)

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
