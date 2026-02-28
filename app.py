import streamlit as st
import fitz  # PyMuPDF

# --- पेज सेटिंग ---
st.set_page_config(page_title="Flipkart Label Cropper", page_icon="📦", layout="wide")

st.title("📦 Flipkart Shipping Label Only")
st.write("अपनी PDF फाइल अपलोड करें, यह अपने आप सिर्फ 'शिपिंग लेबल' वाला हिस्सा निकाल देगा।")

# --- ऑटोमैटिक क्रॉपिंग सेटिंग्स (जैसा आपकी फोटो में है) ---
# शिपिंग लेबल आमतौर पर पेज के ऊपरी 52% हिस्से में होता है
crop_percent = 52  

uploaded_files = st.file_uploader("Flipkart PDF यहाँ अपलोड करें", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            merged_pdf = fitz.open()
            
            for file in uploaded_files:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                # हर फाइल का सिर्फ पहला पेज लें जहाँ लेबल होता है
                page = doc[0]
                
                # थर्मल प्रिंटर के लिए 4x6 इंच (288 x 432 पॉइंट्स) का नया पेज
                new_page = merged_pdf.new_page(width=288, height=432)
                
                # सिर्फ ऊपर का शिपिंग लेबल वाला हिस्सा (Barcode, Address, SKU)
                # साइड के फालतू सफेद हिस्से को हटाने के लिए 15 पॉइंट्स का मार्जिन छोड़ा है
                page_rect = page.rect
                clip_rect = fitz.Rect(15, 15, page_rect.width - 15, page_rect.height * (crop_percent / 100.0))
                
                # कटे हुए लेबल को नए पेज पर एकदम फिट करना
                new_page.show_pdf_page(new_page.rect, doc, 0, clip=clip_rect)
                doc.close()

            pdf_bytes = merged_pdf.write()
            
            st.success(f"✅ {len(uploaded_files)} शिपिंग लेबल तैयार हैं!")
            
            # डाउनलोड और प्रीव्यू
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("### लेबल प्रीव्यू:")
                preview_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pix = preview_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                st.image(pix.tobytes("png"), use_container_width=True)
                
            with col2:
                st.write("### फाइल डाउनलोड करें:")
                st.download_button(
                    label="📥 डाउनलोड शिपिंग लेबल (PDF)",
                    data=pdf_bytes,
                    file_name="Flipkart_Shipping_Labels_Only.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"त्रुटि: {e}")

st.markdown("---")
st.write("Developed for Devilsons & Mechanic37")
