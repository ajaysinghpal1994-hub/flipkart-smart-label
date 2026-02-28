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
# 🖥️ MAIN PAGE (Bulk Upload & Merge)
# ==========================================
st.title("📦 Flipkart Smart Label Pro (Bulk Mode)")
st.write("अपने Flipkart PDF को अपलोड करें। आप **एक साथ कई PDF** (Bulk Upload) चुन सकते हैं।")

# --- फाइल अपलोडर (Multiple Files) ---
# accept_multiple_files=True करने से हम एक साथ कई फाइल डाल सकते हैं
uploaded_files = st.file_uploader("Drop your PDF labels here", type="pdf", accept_multiple_files=True)

if uploaded_files: # अगर फाइलें अपलोड की गई हैं
    with st.spinner(f'प्रोसेसिंग हो रही है ({len(uploaded_files)} फाइल्स)...'):
        try:
            # मर्ज करने के लिए एक नई खाली PDF बनाना
            merged_pdf = fitz.open()
            total_price_sum = 0.0 # टोटल अमाउंट जोड़ने के लिए
            preview_pix = None

            # हर एक अपलोड की गई फाइल पर लूप चलाना
            for index, file in enumerate(uploaded_files):
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                text = page.get_text()

                # कीमत ढूँढें
                price_pattern = r"(Total Price|Grand Total|Total Amount)[:\s]+([\d\.]+)"
                match = re.search(price_pattern, text, re.IGNORECASE)
                final_price = match.group(2) if match else "Check Invoice"

                # टोटल अमाउंट कैलकुलेट करें
                if match:
                    try:
                        total_price_sum += float(final_price)
                    except:
                        pass

                # टेक्स्ट लिखें
                if add_price:
                    display_text = f"Value: Rs. {final_price} (Tax Invoice Inside)"
                    rect = fitz.Rect(pos_x - 5, pos_y - 18, pos_x + 320, pos_y + 5)
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1)) 
                    page.insert_text(fitz.Point(pos_x, pos_y), display_text, fontsize=16, color=(0, 0, 0))

                # क्रॉप करें
                if not keep_invoice:
                    page_rect = page.rect
                    crop_height = page_rect.height * (crop_percent / 100.0)
                    page.set_cropbox(fitz.Rect(0, 0, page_rect.width, crop_height))

                # स्क्रीन पर दिखाने के लिए सिर्फ पहले पेज की फोटो लें
                if index == 0:
                    zoom = 2
                    mat = fitz.Matrix(zoom, zoom)
                    preview_pix = page.get_pixmap(matrix=mat)

                # प्रोसेस किए गए पेज को हमारी फाइनल (Merged) PDF में जोड़ दें
                merged_pdf.insert_pdf(doc)
                doc.close()

            # नई Merged PDF फाइल को सेव करना
            pdf_bytes = merged_pdf.write()
            merged_pdf.close()

            st.success(f"✅ {len(uploaded_files)} PDF सफलतापूर्वक मर्ज हो गए हैं!")

            # --- परिणाम और डाउनलोड बटन ---
            col1, col2 = st.columns([1, 1])
            with col1:
                if preview_pix:
                    st.image(preview_pix.tobytes("png"), caption=f"Preview (Page 1 of {len(uploaded_files)})", use_container_width=True)
            with col2:
                st.write("### 🎉 Your Bulk Label is Ready!")
                st.write(f"**📦 Total Orders Processed:** {len(uploaded_files)}")
                if total_price_sum > 0:
                    st.write(f"**💰 Total Order Value:** Rs. {total_price_sum:.2f}")
                
                st.write("आपकी फाइल प्रिंटर के लिए एकदम तैयार है।")
                st.markdown("<br>", unsafe_allow_html=True) 
                
                st.download_button(
                    label=f"📥 Download Merged PDF ({len(uploaded_files)} Labels)",
                    data=pdf_bytes,
                    file_name=f"Smart_Labels_Merged_{len(uploaded_files)}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"कुछ गड़बड़ हुई: {e}")
