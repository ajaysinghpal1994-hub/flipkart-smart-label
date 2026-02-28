import streamlit as st
import fitz  # PyMuPDF

# --- पेज सेटिंग ---
st.set_page_config(page_title="Flipkart Label Cropper", page_icon="📦", layout="wide")

st.title("📦 Flipkart Perfect Shipping Label Cropper")
st.write("यह टूल आपके लेबल का ओरिजिनल साइज बनाए रखेगा और सिर्फ शिपिंग लेबल क्रॉप करेगा।")

# --- ऑटोमैटिक सेटिंग्स (वही साइज जो आपने मांगा है) ---
crop_percent = 50  

uploaded_files = st.file_uploader("Flipkart PDF यहाँ डालें", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            merged_pdf = fitz.open()
            
            for file in uploaded_files:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                
                # ओरिजिनल पेज का साइज लें ताकि साइज न बदले
                page_rect = page.rect
                
                # सिर्फ ऊपर का 50% हिस्सा क्रॉप करें (Original Width बनाए रखते हुए)
                # यह बिलिंग एड्रेस और इनवॉइस को पूरी तरह हटा देगा
                crop_rect = fitz.Rect(0, 0, page_rect.width, page_rect.height * (crop_percent / 100.0))
                
                # नया पेज जो ओरिजिनल विड्थ और क्रॉप की हुई हाइट का होगा
                new_page = merged_pdf.new_page(width=page_rect.width, height=crop_rect.height)
                
                # ओरिजिनल लेबल को नए पेज पर बिना स्ट्रेच किए रखें
                new_page.show_pdf_page(new_page.rect, doc, 0, clip=crop_rect)
                doc.close()

            pdf_bytes = merged_pdf.write()
            
            st.success(f"✅ {len(uploaded_files)} लेबल तैयार हैं!")
            
            # प्रीव्यू और डाउनलोड
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("### प्रीव्यू (वही साइज जो आपने भेजा):")
                preview_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pix = preview_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                st.image(pix.tobytes("png"), use_container_width=True)
                
            with col2:
                st.write("### डाउनलोड करें:")
                st.download_button(
                    label="📥 डाउनलोड परफेक्ट साइज लेबल (PDF)",
                    data=pdf_bytes,
                    file_name="Flipkart_Perfect_Size_Labels.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"त्रुटि: {e}")

st.markdown("---")
st.write("Developed for Devilsons & Mechanic37")
