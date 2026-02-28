import streamlit as st
import fitz  # PyMuPDF

# --- पेज सेटिंग ---
st.set_page_config(page_title="Flipkart Auto Label Cropper", page_icon="📦", layout="wide")

st.title("📦 Flipkart Automatic Shipping Label Cropper")
st.write("अपनी PDF फाइल अपलोड करें, यह अपने आप सिर्फ शिपिंग लेबल क्रॉप कर देगा।")

# --- ऑटोमैटिक सेटिंग्स ---
crop_percent = 54  # शिपिंग लेबल के लिए परफेक्ट कटिंग प्रतिशत

uploaded_files = st.file_uploader("Flipkart PDF यहाँ अपलोड करें", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            merged_pdf = fitz.open()
            
            for file in uploaded_files:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                
                # ऑटोमैटिक 4x6 थर्मल क्रॉपिंग (बिना प्राइस लिखे)
                new_page = merged_pdf.new_page(width=288, height=432) # 4x6 Size
                
                # लेबल का ऊपरी हिस्सा (शिपिंग एड्रेस और SKU)
                clip_rect = fitz.Rect(15, 15, page.rect.width - 15, page.rect.height * (crop_percent / 100.0))
                
                # उसे नए 4x6 पेज पर फिट करना
                new_page.show_pdf_page(new_page.rect, doc, 0, clip=clip_rect)
                doc.close()

            pdf_bytes = merged_pdf.write()
            
            st.success(f"✅ {len(uploaded_files)} शिपिंग लेबल तैयार हैं!")
            st.download_button(
                label="📥 डाउनलोड क्रॉप्ड लेबल (PDF)",
                data=pdf_bytes,
                file_name="Flipkart_Shipping_Labels.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # प्रीव्यू
            st.write("### लेबल प्रीव्यू:")
            preview_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pix = preview_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
            st.image(pix.tobytes("png"), use_container_width=True)

        except Exception as e:
            st.error(f"त्रुटि: {e}")

st.markdown("---")
st.write("Developed for Devilsons & Mechanic37")
