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
    add_price = st.checkbox("✅ Print Price on Label", value=True, help="यह लेबल पर 'Value: Rs. XX' प्रिंट करेगा।")
    keep_invoice = st.checkbox("📄 Keep Invoice (No Crop)", value=False, help="अगर आप पूरा A4 पेज (बिना काटे) चाहते हैं, तो इसे टिक करें।")
    
    st.markdown("### 📏 Advanced Crop Settings")
    with st.expander("✂️ Adjust Crop & Text Position"):
        st.write("यहाँ से आप टेक्स्ट की जगह और पेज की कटिंग सेट कर सकते हैं:")
        crop_percent = st.slider("✂️ Crop Percentage (%)", 50, 100, 65, disabled=keep_invoice)
        pos_x = st.slider("↔️ X-Axis (Left/Right)", 0, 400, 30, disabled=not add_price)
        pos_y = st.slider("↕️ Y-Axis (Up/Down)", 0, 600, 470, disabled=not add_price)
    
    st.markdown("---")
    st.write("Powered by **Mechanic37 Tech**")


# ==========================================
# 🖥️ MAIN PAGE (Upload & Preview)
# ==========================================
st.title("📦 Flipkart Smart Label Pro")
st.write("अपने Flipkart PDF को अपलोड करें। बाईं तरफ (Sidebar) से अपनी सेटिंग चुनें।")

# --- फाइल अपलोडर (Drag & Drop) ---
uploaded_file = st.file_uploader("Drop your PDF label here", type="pdf")

if uploaded_file is not None:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            # 1. PDF पढ़ें
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            page = doc[0]
            text = page.get_text()

            # 2. कीमत ढूँढें
            price_pattern = r"(Total Price|Grand Total|Total Amount)[:\s]+([\d\.]+)"
            match = re.search(price_pattern, text, re.IGNORECASE)
            final_price = match.group(2) if match else "Check Invoice"

            # 3. अगर "Print Price" टिक है, तो टेक्स्ट लिखें
            if add_price:
                display_text = f"Value: Rs. {final_price} (Tax Invoice Inside)"
                # टेक्स्ट के पीछे सफेद बॉक्स
                rect = fitz.Rect(pos_x - 5, pos_y - 18, pos_x + 320, pos_y + 5)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1)) 
                # ब्लैक टेक्स्ट
                page.insert_text(fitz.Point(pos_x, pos_y), display_text, fontsize=16, color=(0, 0, 0))

            # 4. अगर "Keep Invoice" टिक नहीं है, तो क्रॉप करें (SKU बचाने के लिए)
            if not keep_invoice:
                page_rect = page.rect
                crop_height = page_rect.height * (crop_percent / 100.0)
                page.set_cropbox(fitz.Rect(0, 0, page_rect.width, crop_height))

            # 5. नई PDF फाइल को सेव करना
            pdf_bytes = doc.write()

            st.success("✅ PDF सफलतापूर्वक तैयार हो गई है!")

            # --- परिणाम और डाउनलोड बटन (Professional Look) ---
            col1, col2 = st.columns([1, 1])
            with col1:
                # Preview Image
                zoom = 2
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                st.image(pix.tobytes("png"), caption="Live Preview", use_container_width=True)
            with col2:
                st.write("### 🎉 Your Label is Ready!")
                st.write(f"**Detected Price:** Rs. {final_price}")
                st.write("आपकी फाइल थर्मल प्रिंटर के लिए एकदम सही साइज़ में तैयार है।")
                st.markdown("<br>", unsafe_allow_html=True) # थोड़ा गैप देने के लिए
                st.download_button(
                    label="📥 Download Ready Label (PDF)",
                    data=pdf_bytes,
                    file_name=f"Smart_Label_{final_price}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"कुछ गड़बड़ हुई: {e}")
