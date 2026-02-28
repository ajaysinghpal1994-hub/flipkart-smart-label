import streamlit as st
import fitz  # PyMuPDF

# --- पेज सेटिंग ---
st.set_page_config(page_title="Flipkart Label Cropper", page_icon="📦", layout="wide")

st.title("📦 Flipkart Shipping Label Only (Auto-Crop)")
st.write("अपनी PDF अपलोड करें। यह अपने आप इनवॉइस हटाकर सिर्फ शिपिंग लेबल (4x6) देगा।")

# --- ऑटोमैटिक सेटिंग्स (जैसा आपने कहा) ---
crop_percent = 50  # इनवॉइस हटाने के लिए सटीक कटिंग [cite: 469]

uploaded_files = st.file_uploader("Flipkart PDF यहाँ डालें", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            merged_pdf = fitz.open()
            
            for file in uploaded_files:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                
                # 4x6 इंच (288 x 432 पॉइंट्स) का नया पेज
                new_page = merged_pdf.new_page(width=288, height=432)
                
                # सिर्फ ऊपर का 50% हिस्सा (शिपिंग लेबल) लेना
                page_rect = page.rect
                clip_rect = fitz.Rect(15, 15, page_rect.width - 15, page_rect.height * (crop_percent / 100.0))
                
                # नए पेज पर फिट करना
                new_page.show_pdf_page(new_page.rect, doc, 0, clip=clip_rect)
                doc.close()

            pdf_bytes = merged_pdf.write()
            
            st.success(f"✅ {len(uploaded_files)} लेबल तैयार हैं!")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("### प्रीव्यू:")
                preview_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pix = preview_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                st.image(pix.tobytes("png"), use_container_width=True)
                
            with col2:
                st.write("### डाउनलोड करें:")
                st.download_button(
                    label="📥 डाउनलोड शिपिंग लेबल (PDF)",
                    data=pdf_bytes,
                    file_name="Flipkart_Perfect_Labels.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"त्रुटि: {e}")

st.markdown("---")
st.write("Developed for Devilsons & Mechanic37")
