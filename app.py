import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2
from pyzbar import pyzbar

st.set_page_config(page_title="📷 Barcode Inventory Scanner", layout="centered")
st.title("📦 Inventory Barcode Scanner with Camera")

st.info("👈 افتح الكاميرا ووجهها ناحية الباركود")

# معالجة كل فريم فيديو
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    barcodes = pyzbar.decode(img)
    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        st.session_state["scanned_barcode"] = barcode_data
        break  # ناخد أول باركود ونوقف

    return av.VideoFrame.from_ndarray(img, format="bgr24")

# تشغيل الكاميرا
webrtc_streamer(key="example", video_frame_callback=video_frame_callback)

# النتيجة
if "scanned_barcode" in st.session_state:
    st.success(f"✅ Barcode Scanned: {st.session_state['scanned_barcode']}")
