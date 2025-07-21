import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Inventory Scanner", layout="wide")
st.title("📦 Inventory Scanner App")

uploaded_file = st.file_uploader("Upload your inventory Excel file", type=["xlsx"])

# تحميل الملف ومعالجة التابات
if uploaded_file and "sheets_data" not in st.session_state:
    try:
        # قراءة كل التابات
        xls = pd.ExcelFile(uploaded_file)
        sheets_data = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
        
        # تحقق من الأعمدة في كل تاب
        for name, df in sheets_data.items():
            if "Barcodes" not in df.columns or "Available Quantity" not in df.columns:
                st.error(f"❌ Sheet '{name}' must contain 'Barcodes' and 'Available Quantity'")
                st.stop()
            df["Actual Quantity"] = 0
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]

        st.session_state.sheets_data = sheets_data
        st.session_state.selected_sheet = xls.sheet_names[0]
        st.session_state.df = sheets_data[st.session_state.selected_sheet]

        st.success("✅ File loaded successfully!")
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        st.stop()

# بعد تحميل الملف
if "sheets_data" in st.session_state:
    # اختيار التاب
    sheet_names = list(st.session_state.sheets_data.keys())
    selected = st.selectbox("Select Sheet (Brand)", sheet_names, index=sheet_names.index(st.session_state.selected_sheet))
    
    if selected != st.session_state.selected_sheet:
        st.session_state.selected_sheet = selected
        st.session_state.df = st.session_state.sheets_data[selected]

    df = st.session_state.df

    st.subheader("📸 Scan Barcode")
    barcode = st.text_input("Scan or enter barcode", key="barcode_input")

    if barcode:
        barcode = barcode.strip()
        if barcode in df["Barcodes"].astype(str).values:
            df.loc[df["Barcodes"].astype(str) == barcode, "Actual Quantity"] += 1
            df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
            st.success(f"✅ Barcode {barcode} counted.")
        else:
            st.warning(f"❌ Barcode '{barcode}' not found.")

        st.session_state.barcode_input = ""  # تفريغ الحقل
        st.experimental_rerun()

    st.dataframe(df, use_container_width=True)

    # زر التحميل
    if "sheets_data" in st.session_state:
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
