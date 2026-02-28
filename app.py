import streamlit as st
import fitz  # PyMuPDF
import re

# --- पेज की सेटिंग ---
st.set_page_config(page_title="Flipkart Smart Label Merger", page_icon="📦", layout="centered")

st.title("📦 Flipkart Smart Label Merger (PDF Version)")
st.write("अपने Flipkart PDF को अपलोड करें। यह उसमें 'Price' जोड़कर आपको वापस PDF फाइल ही देगा।")

# --- सेटिंग स्लाइडर्स ---
st.write("### ⚙️ सेटिंग (टेक्स्ट की जगह और कटिंग सेट करें)")
col_x, col_y, col_crop = st.columns(3)
with col_x:
    pos_x = st.slider("↔️ बाएँ/दाएँ (X)", 0, 400, 30) 
with col_y:
    pos_y = st.slider("↕️ ऊपर/नीचे (Y)", 0, 600, 470)
with col_crop:
    # 65% रखने पर आमतौर पर SKU नहीं कटता
    crop_percent = st.slider("✂️ कितना काटना है (%)", 50, 100, 65) 

# --- फाइल अपलोडर ---
uploaded_file = st.file_uploader("अपना PDF लेबल यहाँ डालें", type="pdf")

if uploaded_file is not None:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            # 1. PDF पढ़ें (बिना इमेज में बदले)
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            page = doc[0]
            text = page.get_text()

            # 2. कीमत ढूँढें
            price_pattern = r"(Total Price|Grand Total|Total Amount)[:\s]+([\d\.]+)"
            match = re.search(price_pattern, text, re.IGNORECASE)
            final_price = match.group(2) if match else "Check Invoice"

            # 3. PDF में सीधे टेक्स्ट लिखना
            display_text = f"Value: Rs. {final_price} (Tax Invoice Inside)"
            
            # टेक्स्ट के पीछे एक सफेद बॉक्स बनाना (ताकि पीछे की लाइन छिप जाए)
            # Box Coordinates (x0, y0, x1, y1)
            rect = fitz.Rect(pos_x - 5, pos_y - 18, pos_x + 320, pos_y + 5)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1)) 
            
            # डार्क और बोल्ड टेक्स्ट लिखना (helv-bo = Helvetica Bold)
            page.insert_text(fitz.Point(pos_x, pos_y), display_text, fontsize=16, fontname="helv-bo", color=(0, 0, 0))

            # 4. PDF को काटना (Crop) - SKU बचाने के लिए
            page_rect = page.rect
            crop_height = page_rect.height * (crop_percent / 100.0)
            # नया क्रॉप बॉक्स सेट करें
            page.set_cropbox(fitz.Rect(0, 0, page_rect.width, crop_height))

            # 5. नई PDF फाइल को सेव करना
            pdf_bytes = doc.write()

            st.success("✅ PDF तैयार है! अब आपका SKU नहीं कटेगा।")

            # --- परिणाम दिखाना ---
            col1, col2 = st.columns(2)
            with col1:
                # स्क्रीन पर दिखाने के लिए इमेज बना रहे हैं, लेकिन डाउनलोड PDF ही होगा
                zoom = 2
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                st.image(pix.tobytes("png"), caption="PDF Preview (चेक करें)", use_container_width=True)
            with col2:
                st.write("### यहाँ से डाउनलोड करें")
                st.download_button(
                    label="📥 डाउनलोड लेबल (PDF)",
                    data=pdf_bytes,
                    file_name=f"Smart_Label_{final_price}.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"कुछ गड़बड़ हुई: {e}")

st.markdown("---")
st.write("Developed with ❤️ by Mechanic37 & Devilson")
