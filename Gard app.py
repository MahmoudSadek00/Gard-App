import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Domanza Inventory App", layout="wide")
st.title("📦 Domanza Inventory App")
st.markdown("### اسكان الباركود وإدارة الجرد")

# رفع ملف Excel
uploaded_file = st.file_uploader("ارفع ملف Excel يحتوي على الشيتات (براندات)", type=["xlsx"])

if uploaded_file:
    # قراءة الشيتات
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    # اختيار الشيت
    selected_sheet = st.selectbox("اختار البراند", sheet_names)

    if selected_sheet:
        df = xls.parse(selected_sheet)

        # التحقق من الأعمدة المطلوبة
        if not {"Barcodes", "Available Quantity"}.issubset(df.columns):
            st.error("❌ الشيت لازم يحتوي على الأعمدة: Barcodes و Available Quantity")
            st.stop()

        # تهيئة session_state
        if "scanned_data" not in st.session_state or st.session_state.get("active_sheet") != selected_sheet:
            st.session_state.active_sheet = selected_sheet
            columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Difference"]
            st.session_state.scanned_data = pd.DataFrame(columns=columns)

        # إدخال الباركود
        barcode = st.text_input("📷 Scan Barcode", key="barcode_input")

        if barcode:
            # التحقق من وجود الباركود
            match = df[df["Barcodes"] == barcode]
            if not match.empty:
                barcode_value = barcode
                available_qty = match.iloc[0]["Available Quantity"]

                # هل الباركود ده اتسجل قبل كده؟
                existing = st.session_state.scanned_data["Barcodes"] == barcode_value
                if existing.any():
                    st.session_state.scanned_data.loc[existing, "Actual Quantity"] += 1
                    st.session_state.scanned_data.loc[existing, "Difference"] = (
                        st.session_state.scanned_data.loc[existing, "Actual Quantity"] - available_qty
                    )
                else:
                    new_row = {
                        "Barcodes": barcode_value,
                        "Available Quantity": available_qty,
                        "Actual Quantity": 1,
                        "Difference": 1 - available_qty
                    }
                    st.session_state.scanned_data = pd.concat(
                        [st.session_state.scanned_data, pd.DataFrame([new_row])],
                        ignore_index=True
                    )
            else:
                st.warning("⚠️ الباركود غير موجود في الشيت")

            # تفريغ خانة الباركود وإعادة تشغيل الصفحة
            st.experimental_rerun()

        # عرض الجدول المحدث
        st.dataframe(st.session_state.scanned_data, use_container_width=True)

        # زر التحميل
        st.download_button(
            label="⬇️ تحميل الجرد",
            data=st.session_state.scanned_data.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{selected_sheet}_inventory.csv",
            mime="text/csv"
        )
else:
    st.info("📂 من فضلك ارفع ملف Excel يحتوي على Barcodes و Available Quantity")
