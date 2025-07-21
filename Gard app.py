import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Domanza Inventory App", layout="wide")

st.title("📦 Domanza Inventory App")
st.markdown("### اسكان الباركود وإدارة الجرد")

# رفع ملف الإكسل
uploaded_file = st.file_uploader("ارفع ملف يحتوي على الأعمدة: Barcodes و Available Quantity", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # تأكد من وجود الأعمدة المطلوبة
        if not {"Barcodes", "Available Quantity"}.issubset(df.columns):
            st.error("❌ الشيت لازم يحتوي على الأعمدة: Barcodes و Available Quantity")
            st.stop()

        # تهيئة session_state لتخزين النتائج
        if "scanned_data" not in st.session_state:
            columns = df.columns.tolist() + ["Actual Quantity", "Difference"]
            columns = list(dict.fromkeys(columns))  # إزالة الأعمدة المكررة
            st.session_state.scanned_data = pd.DataFrame(columns=columns)

        # إدخال الباركود
        barcode = st.text_input("📷 Scan Barcode", key="barcode_input")

        if barcode:
            # البحث عن الباركود
            match = df[df["Barcodes"] == barcode]
            if not match.empty:
                row = match.iloc[0].to_dict()
                row["Actual Quantity"] = 1
                row["Difference"] = row["Actual Quantity"] - row["Available Quantity"]

                new_row_df = pd.DataFrame([row])
                new_row_df = new_row_df.loc[:, ~new_row_df.columns.duplicated()]  # إزالة الأعمدة المكررة

                st.session_state.scanned_data = pd.concat([
                    st.session_state.scanned_data,
                    new_row_df
                ], ignore_index=True)

            else:
                st.warning("⚠️ الباركود غير موجود في الشيت")

            # تفريغ خانة الباركود بعد كل مسح
            st.experimental_rerun()

        # عرض البيانات الممسوحة
        if not st.session_state.scanned_data.empty:
            st.dataframe(st.session_state.scanned_data, use_container_width=True)

            # تحميل النتائج
            st.download_button(
                label="⬇️ تحميل النتائج كـ Excel",
                data=st.session_state.scanned_data.to_csv(index=False).encode("utf-8-sig"),
                file_name="scanned_inventory.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.info("📂 من فضلك ارفع ملف Excel أولاً")
