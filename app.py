import streamlit as st
import fitz  # PyMuPDF

# --- पेज सेटिंग ---
st.set_page_config(page_title="Flipkart Perfect Label", page_icon="📦", layout="wide")

st.title("📦 Flipkart Perfect Shipping Label (Clean Crop)")
st.write("यह टूल बिंदीदार लाइन (Dashed Line) के नीचे का सारा हिस्सा हटाकर सिर्फ शिपिंग लेबल देगा।")

# --- सटीक कटिंग (47% करने से बिंदीदार लाइन के नीचे का हिस्सा पूरी तरह कट जाएगा) ---
crop_percent = 47  

uploaded_files = st.file_uploader("Flipkart PDF यहाँ डालें", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            merged_pdf = fitz.open()
            
            for file in uploaded_files:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                page_rect = page.rect
                
                # सटीक क्रॉप बॉक्स (Dashed line के ठीक ऊपर तक)
                crop_rect = fitz.Rect(0, 0, page_rect.width, page_rect.height * (crop_percent / 100.0))
                
                # नया पेज (Original Width के साथ)
                new_page = merged_pdf.new_page(width=page_rect.width, height=crop_rect.height)
                
                # ओरिजिनल लेबल को बिना स्ट्रेच किए फिट करना
                new_page.show_pdf_page(new_page.rect, doc, 0, clip=crop_rect)
                doc.close()

            pdf_bytes = merged_pdf.write()
            
            st.success(f"✅ {len(uploaded_files)} लेबल एकदम सटीक क्रॉप हो गए हैं!")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("### प्रीव्यू (चेक करें कि नीचे का हिस्सा कट गया है):")
                preview_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pix = preview_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                st.image(pix.tobytes("png"), use_container_width=True)
                
            with col2:
                st.write("### डाउनलोड करें:")
                st.download_button(
                    label="📥 डाउनलोड क्लीन शिपिंग लेबल (PDF)",
                    data=pdf_bytes,
                    file_name="Flipkart_Clean_Shipping_Labels.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"त्रुटि: {e}")

st.markdown("---")
st.write("Developed for Devilsons & Mechanic37")
