import streamlit as st
import fitz  # PyMuPDF
import re

# --- पेज की सेटिंग (Wide Layout for Pro Look) ---
st.set_page_config(page_title="Flipkart Smart Label Pro", page_icon="📦", layout="wide")

# ==========================================
# ⚙️ SIDEBAR SETTINGS (PDFCroppers Style)
# ==========================================
with st.sidebar:
    st.title("⚙️ Label Settings")
    st.markdown("अपनी जरूरत के हिसाब से सेटिंग चुनें:")
    
    st.markdown("### 🛠️ Basic Features")
    add_price = st.checkbox("✅ Print Price on Label", value=True)
    thermal_format = st.checkbox("🖨️ 4x6 Thermal Printer Format", value=True, help="यह फालतू सफेद मार्जिन हटाकर बिल्कुल 4x6 इंच का परफेक्ट थर्मल साइज बनाएगा।")
    keep_invoice = st.checkbox("📄 Keep Invoice (No Crop)", value=False, disabled=thermal_format, help="A4 साइज में रखने के लिए इसे चुनें (थर्मल मोड बंद करना होगा)।")
    
    st.markdown("### 📏 Advanced Crop Settings")
    with st.expander("✂️ Adjust Crop & Text Position"):
        st.write("टेक्स्ट की जगह और पेज की कटिंग सेट करें:")
        # थर्मल के लिए डिफ़ॉल्ट 60% सही रहता है
        crop_percent = st.slider("✂️ Crop Percentage (%)", 40, 100, 60, disabled=keep_invoice and not thermal_format)
        pos_x = st.slider("↔️ X-Axis (Left/Right)", 0, 400, 30, disabled=not add_price)
        pos_y = st.slider("↕️ Y-Axis (Up/Down)", 0, 600, 470, disabled=not add_price)
    
    st.markdown("---")
    st.write("Powered by **Mechanic37 Tech**")


# ==========================================
# 🖥️ MAIN PAGE (Bulk Upload + 4x6 Thermal)
# ==========================================
st.title("📦 Flipkart Smart Label Pro (Bulk + Thermal)")
st.write("अपने Flipkart PDF अपलोड करें। यह एक साथ कई फाइलों को **मर्ज** करेगा और **थर्मल प्रिंटर (4x6)** के लिए परफेक्ट साइज बनाएगा।")

# --- फाइल अपलोडर (Multiple Files) ---
uploaded_files = st.file_uploader("Drop your PDF labels here", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner(f'प्रोसेसिंग हो रही है ({len(uploaded_files)} फाइल्स)...'):
        try:
            merged_pdf = fitz.open()
            total_price_sum = 0.0
            preview_pix = None

            for index, file in enumerate(uploaded_files):
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                text = page.get_text()
                page_rect = page.rect

                # 1. कीमत ढूँढें
                price_pattern = r"(Total Price
