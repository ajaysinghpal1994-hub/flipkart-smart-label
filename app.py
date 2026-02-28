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
    add_price = st.checkbox("✅ Print Price on Label", value=True)
    thermal_format = st.checkbox("🖨️ 4x6 Thermal Printer Format", value=True, help="यह फालतू सफेद मार्जिन हटाकर बिल्कुल 4x6 इंच का परफेक्ट थर्मल साइज बनाएगा।")
    keep_invoice = st.checkbox("📄 Keep Invoice (No Crop)", value=False, disabled=thermal_format, help="A4 साइज में रखने के लिए इसे चुनें (थर्मल मोड बंद करना होगा)।")
    
    st.markdown("### 📏 Advanced Crop Settings")
    with st.expander("✂️ Adjust Crop & Text Position"):
        st.write("टेक्स्ट की जगह और पेज की कटिंग सेट करें:")
        # थर्मल के लिए डिफ़ॉल्ट 60% सही रहता है
        crop_percent = st.slider("✂️ Crop Percentage (%)", 40, 100, 60, disabled=keep_invoice and not thermal_format)
        pos_x = st.slider("↔️ X-Axis (Left/Right)", 0, 400, 30, disabled=not add_price)
        pos_y = st.slider("↕️ Y-Axis (Up/Down)", 0, 600, 470, disabled=not add_price)
    
    st.markdown("---")
    st.write("Powered by **Mechanic37 Tech**")


# ==========================================
# 🖥️ MAIN PAGE (Bulk Upload + 4x6 Thermal)
# ==========================================
st.title("📦 Flipkart Smart Label Pro (Bulk + Thermal)")
st.write("अपने Flipkart PDF अपलोड करें। यह एक साथ कई फाइलों को **मर्ज** करेगा और **थर्मल प्रिंटर (4x6)** के लिए परफेक्ट साइज बनाएगा।")

# --- फाइल अपलोडर (Multiple Files) ---
uploaded_files = st.file_uploader("Drop your PDF labels here", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.spinner(f'प्रोसेसिंग हो रही है ({len(uploaded_files)} फाइल्स)...'):
        try:
            merged_pdf = fitz.open()
            total_price_sum = 0.0
            preview_pix = None

            for index, file in enumerate(uploaded_files):
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc[0]
                text = page.get_text()
                page_rect = page.rect

                # 1. कीमत ढूँढें
                price_pattern = r"(Total Price|Grand Total|Total Amount)[:\s]+([\d\.]+)"
                match = re.search(price_pattern, text, re.IGNORECASE)
                final_price = match.group(2) if match else "Check Invoice"

                if match:
                    try:
                        total_price_sum += float(final_price)
                    except:
                        pass

                # 2. कीमत लिखें
                if add_price:
                    display_text = f"Value: Rs. {final_price} (Tax Invoice Inside)"
                    rect = fitz.Rect(pos_x - 5, pos_y - 18, pos_x + 320, pos_y + 5)
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1)) 
                    page.insert_text(fitz.Point(pos_x, pos_y), display_text, fontsize=16, color=(0, 0, 0))

                # 3. 4x6 इंच थर्मल प्रिंटर फॉर्मेट
                if thermal_format:
                    # 4x6 इंच को पॉइंट्स में बदलें (1 इंच = 72 पॉइंट्स) -> 288 x 432
                    new_page = merged_pdf.new_page(width=288, height=432)
                    
                    # Flipkart लेबल के साइड के सफेद मार्जिन हटाएं (x=15 से width-15)
                    crop_height = page_rect.height * (crop_percent / 100.0)
                    clip_rect = fitz.Rect(15, 15, page_rect.width - 15, crop_height)
                    
                    # कटे हुए हिस्से को नई 4x6 पेज पर स्ट्रेच/फिट कर दें
                    new_page.show_pdf_page(new_page.rect, doc, 0, clip=clip_rect)
                    
                    # प्रीव्यू के लिए
                    if index == 0:
                        mat = fitz.Matrix(2, 2)
                        preview_pix = new_page.get_pixmap(matrix=mat)
                
                # 4. नॉर्मल मोड (अगर थर्मल टिक नहीं है)
                else:
                    if not keep_invoice:
                        crop_height = page_rect.height * (crop_percent / 100.0)
                        page.set_cropbox(fitz.Rect(0, 0, page_rect.width, crop_height))
                    
                    merged_pdf.insert_pdf(doc)
                    
                    if index == 0:
                        mat = fitz.Matrix(2, 2)
                        preview_pix = merged_pdf[0].get_pixmap(matrix=mat)

                doc.close()

            # नई Merged PDF फाइल को सेव करना
            pdf_bytes = merged_pdf.write()
            merged_pdf.close()

            st.success(f"✅ {len(uploaded_files)} PDF सफलतापूर्वक प्रोसेस और मर्ज हो गए हैं!")

            # --- परिणाम और डाउनलोड बटन ---
            col1, col2 = st.columns([1, 1])
            with col1:
                if preview_pix:
                    st.image(preview_pix.tobytes("png"), caption=f"Thermal 4x6 Preview (Page 1)", use_container_width=True)
            with col2:
                st.write("### 🎉 Your Thermal Labels are Ready!")
                st.write(f"**📦 Total Orders:** {len(uploaded_files)}")
                if total_price_sum > 0:
                    st.write(f"**💰 Total Order Value:** Rs. {total_price_sum:.2f}")
                
                st.download_button(
                    label=f"📥 Download 4x6 Thermal PDF",
                    data=pdf_bytes,
                    file_name=f"Smart_Labels_4x6_Merged.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"कुछ गड़बड़ हुई: {e}")

st.markdown("---")
st.write("Developed with ❤️ by Mechanic37 & Devilson")
