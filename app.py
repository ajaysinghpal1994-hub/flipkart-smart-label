import streamlit as st
import fitz  # PyMuPDF

# --- पेज सेटिंग ---
st.set_page_config(page_title="Flipkart Clean Label", page_icon="📦", layout="wide")

st.title("📦 Flipkart Final Clean Label (No Dashed Line)")
st.write("यह वर्जन बिंदीदार लाइन और उसके नीचे के हिस्से को पूरी तरह से काट देगा।")

# --- अब इसे 44% पर सेट किया है ताकि नीचे की लाइन बिल्कुल न आए ---
crop_percent = 44.0  

uploaded_files = st.file_uploader("Flipkart PDF यहाँ अपलोड करें", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            merged_pdf = fitz.open()
            
            for file in uploaded_files:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                page_rect = page.rect
                
                # ओरिजिनल विड्थ के साथ और भी छोटा क्रॉप बॉक्स
                crop_rect = fitz.Rect(0, 0, page_rect.width, page_rect.height * (crop_percent / 100.0))
                
                # नया पेज बनाना (बिना किसी स्ट्रेचिंग के)
                new_page = merged_pdf.new_page(width=page_rect.width, height=crop_rect.height)
                
                # लेबल को ओरिजिनल साइज में रखना
                new_page.show_pdf_page(new_page.rect, doc, 0, clip=crop_rect)
                doc.close()

            pdf_bytes = merged_pdf.write()
            
            st.success(f"✅ {len(uploaded_files)} लेबल्स पूरी तरह से साफ हो गए हैं!")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("### क्लीन प्रीव्यू:")
                preview_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pix = preview_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                st.image(pix.tobytes("png"), use_container_width=True)
                
            with col2:
                st.write("### डाउनलोड करें:")
                st.download_button(
                    label="📥 डाउनलोड परफेक्ट क्लीन लेबल (PDF)",
                    data=pdf_bytes,
                    file_name="Flipkart_Final_Clean_Labels.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"त्रुटि: {e}")

st.markdown("---")
st.write("Developed for Devilsons & Mechanic37")
