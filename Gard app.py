import streamlit as st
import pandas as pd
from PIL import Image
import cv2
from pyzbar.pyzbar import decode
import numpy as np
from io import BytesIO

# إعدادات الصفحة
st.set_page_config(
    page_title="📦 نظام جرد المخزون المتكامل",
    layout="wide",
    page_icon="📊"
)

# تخصيص التصميم
st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    .stButton>button {background-color: #4CAF50; color: white;}
    .stTextInput>div>div>input {text-align: center; font-size: 18px;}
    .metric-box {padding: 15px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    </style>
""", unsafe_allow_html=True)

# حالة الجلسة
if 'barcode_counts' not in st.session_state:
    st.session_state.barcode_counts = {}
if 'barcode_input' not in st.session_state:
    st.session_state.barcode_input = ""
if 'df' not in st.session_state:
    st.session_state.df = None
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'last_scanned' not in st.session_state:
    st.session_state.last_scanned = None

# عنوان التطبيق
st.title("📊 نظام جرد المخزون المتكامل")
st.markdown("---")

# قسم تحميل الملف
with st.expander("📤 تحميل ملف المخزون", expanded=True):
    uploaded_file = st.file_uploader("رفع ملف Excel للمخزون", type=["xlsx"], help="يجب أن يحتوي الملف على أعمدة: الباركود، الكمية المتاحة، الكمية الفعلية، اسم المنتج")
    
    if uploaded_file and st.session_state.df is None:
        try:
            all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
            sheet_names = list(all_sheets.keys())
            
            if len(sheet_names) > 1:
                selected_sheet = st.selectbox("اختر ورقة العمل", sheet_names)
            else:
                selected_sheet = sheet_names[0]
            
            df = all_sheets[selected_sheet]
            df.columns = df.columns.str.strip()

            required_columns = ["Barcodes", "Available Quantity", "Actual Quantity", "Product Name"]
            if not all(col in df.columns for col in required_columns):
                st.error(f"❌ الملف يجب أن يحتوي على الأعمدة التالية: {required_columns}")
                st.info("الأعمدة المتوفرة: " + ", ".join(df.columns.tolist()))
                st.stop()

            # تنظيف البيانات
            df["Barcodes"] = df["Barcodes"].astype(str).str.strip()
            df["Actual Quantity"] = pd.to_numeric(df["Actual Quantity"], errors='coerce').fillna(0).astype(int)
            df["Available Quantity"] = pd.to_numeric(df["Available Quantity"], errors='coerce').fillna(0).astype(int)
            
            st.session_state.df = df.copy()
            st.success("✔ تم تحميل ملف المخزون بنجاح!")
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء تحميل الملف: {str(e)}")
            st.stop()

# إذا تم تحميل البيانات
if st.session_state.df is not None:
    df = st.session_state.df
    
    # إحصاءات سريعة
    st.markdown("### 📊 إحصائيات المخزون")
    col1, col2, col3, col4 = st.columns(4)
    
    total_products = len(df)
    to_restock = len(df[df["Difference"] < 0]) if "Difference" in df.columns else 0
    overstock = len(df[df["Difference"] > 0]) if "Difference" in df.columns else 0
    scanned_items = len(st.session_state.barcode_counts)
    
    col1.markdown(f'<div class="metric-box"><h4>🛍️ إجمالي المنتجات</h4><h2>{total_products}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-box"><h4>⚠ يحتاج إعادة تخزين</h4><h2>{to_restock}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-box"><h4>📦 فائض مخزون</h4><h2>{overstock}</h2></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="metric-box"><h4>📌 العناصر الممسوحة</h4><h2>{scanned_items}</h2></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # قسم المسح
    st.markdown("### 📸 مسح الباركود")
    
    # خيارات المسح
    scan_option = st.radio("طريقة المسح", ["كاميرا الويب", "إدخال يدوي"], horizontal=True)
    
    if scan_option == "كاميرا الويب":
        st.session_state.camera_active = st.checkbox("تفعيل الكاميرا", value=st.session_state.camera_active)
        
        if st.session_state.camera_active:
            img_file_buffer = st.camera_input("وجه الكاميرا نحو الباركود")
            
            if img_file_buffer is not None:
                try:
                    # تحويل الصورة إلى تنسيق OpenCV
                    image = Image.open(img_file_buffer)
                    img_array = np.array(image)
                    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                    
                    # قراءة الباركود
                    barcodes = decode(gray)
                    if barcodes:
                        scanned = barcodes[0].data.decode("utf-8")
                        st.session_state.barcode_input = scanned
                        st.session_state.last_scanned = scanned
                        st.experimental_rerun()
                    else:
                        st.warning("لم يتم التعرف على باركود، حاول مرة أخرى")
                
                except Exception as e:
                    st.error(f"خطأ في معالجة الصورة: {e}")
    
    else:  # الإدخال اليدوي
        scanned = st.text_input(
            "أدخل الباركود يدوياً أو استخدم الماسح الضوئي",
            value=st.session_state.barcode_input,
            key="manual_input"
        )
        
        if scanned:
            st.session_state.last_scanned = scanned.strip()
            st.session_state.barcode_input = ""
            st.experimental_rerun()
    
    # معالجة الباركود الممسوح
    if st.session_state.last_scanned:
        scanned = st.session_state.last_scanned
        
        # البحث عن المنتج
        product_info = df[df["Barcodes"] == scanned]
        
        if not product_info.empty:
            product_name = product_info["Product Name"].values[0]
            current_qty = product_info["Actual Quantity"].values[0]
            
            # عرض معلومات المنتج
            st.markdown(f"""
                <div style="padding: 1rem; background-color: #e8f5e9; border-radius: 10px; margin: 1rem 0;">
                    <h4>🏷️ {product_name}</h4>
                    <p><strong>الباركود:</strong> {scanned}</p>
                    <p><strong>الكمية الحالية:</strong> {current_qty}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # التحكم في الكمية
            col1, col2, col3 = st.columns([1,1,2])
            
            with col1:
                if st.button("➕ زيادة الكمية"):
                    if scanned in st.session_state.barcode_counts:
                        st.session_state.barcode_counts[scanned] += 1
                    else:
                        st.session_state.barcode_counts[scanned] = current_qty + 1
                    
                    df.loc[df["Barcodes"] == scanned, "Actual Quantity"] = st.session_state.barcode_counts[scanned]
                    st.session_state.df = df
                    st.experimental_rerun()
            
            with col2:
                if st.button("➖ تخفيض الكمية"):
                    if scanned in st.session_state.barcode_counts and st.session_state.barcode_counts[scanned] > 0:
                        st.session_state.barcode_counts[scanned] -= 1
                        df.loc[df["Barcodes"] == scanned, "Actual Quantity"] = st.session_state.barcode_counts[scanned]
                        st.session_state.df = df
                        st.experimental_rerun()
                    else:
                        st.warning("الكمية لا يمكن أن تكون أقل من الصفر")
            
            with col3:
                new_qty = st.number_input("تعيين الكمية يدوياً", min_value=0, value=current_qty, key=f"qty_{scanned}")
                if st.button("💾 حفظ الكمية"):
                    st.session_state.barcode_counts[scanned] = new_qty
                    df.loc[df["Barcodes"] == scanned, "Actual Quantity"] = new_qty
                    st.session_state.df = df
                    st.success("تم تحديث الكمية بنجاح!")
                    st.experimental_rerun()
        
        else:
            st.error("⚠ الباركود غير موجود في قاعدة البيانات")
            if st.button("إضافة باركود جديد إلى القائمة"):
                new_product = {
                    "Barcodes": scanned,
                    "Product Name": "منتج جديد",
                    "Available Quantity": 0,
                    "Actual Quantity": 1,
                    "Difference": 1
                }
                
                new_row = pd.DataFrame([new_product])
                df = pd.concat([df, new_row], ignore_index=True)
                st.session_state.df = df
                st.session_state.barcode_counts[scanned] = 1
                st.success("تمت إضافة المنتج الجديد!")
                st.experimental_rerun()
        
        st.session_state.last_scanned = None
    
    st.markdown("---")
    
    # تحديث الفرق
    df["Difference"] = df["Actual Quantity"] - df["Available Quantity"]
    
    # قسم البيانات
    st.markdown("### 📋 بيانات المخزون")
    
    # تصفية البيانات
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        filter_status = st.selectbox("تصفية حسب الحالة", ["الكل", "بحاجة لإعادة تخزين", "فائض مخزون", "متوازن"])
    
    with filter_col2:
        search_query = st.text_input("بحث بالاسم أو الباركود")
    
    # تطبيق الفلاتر
    filtered_df = df.copy()
    
    if filter_status == "بحاجة لإعادة تخزين":
        filtered_df = filtered_df[filtered_df["Difference"] < 0]
    elif filter_status == "فائض مخزون":
        filtered_df = filtered_df[filtered_df["Difference"] > 0]
    elif filter_status == "متوازن":
        filtered_df = filtered_df[filtered_df["Difference"] == 0]
    
    if search_query:
        search_query = search_query.lower()
        filtered_df = filtered_df[
            filtered_df["Product Name"].str.lower().str.contains(search_query) |
            filtered_df["Barcodes"].astype(str).str.contains(search_query)
        ]
    
    # عرض الجدول
    st.dataframe(
        filtered_df.style.applymap(
            lambda x: 'background-color: #ffcccc' if x < 0 else ('background-color: #ccffcc' if x > 0 else ''),
            subset=['Difference']
        ),
        use_container_width=True,
        height=600
    )
    
    st.markdown("---")
    
    # سجل المسح
    st.markdown("### 📝 سجل الباركودات الممسوحة")
    
    if st.session_state.barcode_counts:
        scan_log = pd.DataFrame([
            {
                "الباركود": k,
                "الكمية الممسوحة": v,
                "اسم المنتج": df[df["Barcodes"] == k]["Product Name"].values[0] if k in df["Barcodes"].values else "غير معروف",
                "الفرق": df[df["Barcodes"] == k]["Difference"].values[0] if k in df["Barcodes"].values else 0
            }
            for k, v in st.session_state.barcode_counts.items()
        ])
        
        st.dataframe(scan_log, use_container_width=True)
        
        if st.button("🗑️ مسح السجل"):
            st.session_state.barcode_counts = {}
            st.success("تم مسح سجل المسح بنجاح!")
            st.experimental_rerun()
    else:
        st.info("لا توجد باركودات ممسوحة بعد")
    
    st.markdown("---")
    
    # أدوات التصدير
    st.markdown("### 📤 تصدير البيانات")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        export_format = st.selectbox("تنسيق التصدير", ["Excel", "CSV"])
    
    with export_col2:
        export_all = st.checkbox("تصدير جميع البيانات (بدون تصفية)")
    
    if export_all:
        data_to_export = df
    else:
        data_to_export = filtered_df
    
    if export_format == "Excel":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data_to_export.to_excel(writer, index=False, sheet_name='Inventory')
        excel_data = output.getvalue()
        st.download_button(
            label="📥 تحميل ملف Excel",
            data=excel_data,
            file_name="inventory_report.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        csv_data = data_to_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 تحميل ملف CSV",
            data=csv_data,
            file_name="inventory_report.csv",
            mime="text/csv"
        )

# رسالة إذا لم يتم تحميل ملف
else:
    st.markdown("""
        <div style="text-align: center; padding: 5rem; background-color: #f5f5f5; border-radius: 10px;">
            <h3>مرحباً بكم في نظام جرد المخزون</h3>
            <p>لبدء الاستخدام، يرجى رفع ملف Excel للمخزون من الأعلى</p>
            <p>تأكد أن الملف يحتوي على أعمدة: الباركود، الكمية المتاحة، الكمية الفعلية، اسم المنتج</p>
        </div>
    """, unsafe_allow_html=True)
