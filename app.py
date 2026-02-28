import streamlit as st
import fitz  # PyMuPDF

# --- पेज सेटिंग ---
st.set_page_config(page_title="Flipkart Label Cropper", page_icon="📦", layout="wide")

st.title("📦 Flipkart Perfect Fit Label (No White Space)")
st.write("यह टूल बिंदीदार लाइन और नीचे के सारे सफेद खाली हिस्से को हटा देगा।")

# --- सटीक कटिंग (बिंदीदार लाइन के ठीक ऊपर) ---
crop_percent = 44.7  

uploaded_files = st.file_uploader("Flipkart PDF यहाँ अपलोड करें", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner('प्रोसेसिंग हो रही है...'):
        try:
            merged_pdf = fitz.open()
            
            for file in uploaded_files:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                page_rect = page.rect
                
                # 1. सिर्फ काम के हिस्से का बॉक्स बनाएं (Width वही रहेगी, Height कम हो जाएगी)
                target_height = page_rect.height * (crop_percent / 100.0)
                crop_rect = fitz.Rect(0, 0, page_rect.width, target_height)
                
                # 2. नया पेज ठीक उतनी ही ऊंचाई (target_height) का बनाएं जितना लेबल है
                # इससे नीचे का सफेद हिस्सा अपने आप खत्म हो जाएगा
                new_page = merged_pdf.new_page(width=page_rect.width, height=target_height)
                
                # 3. लेबल को नए छोटे पेज पर रखें
                new_page.show_pdf_page(new_page.rect, doc, 0, clip=crop_rect)
                doc.close()

            pdf_bytes = merged_pdf.write()
            
            st.success(f"✅ {len(uploaded_files)} लेबल अब एकदम फिट साइज में तैयार हैं!")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("### फिट प्रीव्यू (चेक करें):")
                preview_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pix = preview_doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                st.image(pix.tobytes("png"), use_container_width=True)
                
            with col2:
                st.write("### डाउनलोड करें:")
                st.download_button(
                    label="📥 डाउनलोड फिट लेबल (PDF)",
                    data=pdf_bytes,
                    file_name="Flipkart_Final_Fit_Labels.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"त्रुटि: {e}")

st.markdown("---")
st.write("Developed for Devilsons & Mechanic37")
