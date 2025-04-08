import streamlit as st
from PIL import Image
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import base64

# Page config
st.set_page_config(page_title="ImageFit PDF Maker", layout="centered")

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load JS if exists
if os.path.exists("script.js"):
    with open("script.js") as js_file:
        js_code = js_file.read()
    st.markdown(f"<script>{js_code}</script>", unsafe_allow_html=True)

# Title
st.markdown("<h1>ImageFit PDF Maker</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)

# Init session state
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []

# File uploader
uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Add uploaded files
if uploaded_files:
    for f in uploaded_files:
        if f not in st.session_state.selected_files:
            st.session_state.selected_files.append(f)

# Layout size
layout_map = {
    "Very Small (4 per row)": 4,
    "Small (3 per row)": 3,
    "Medium (2 per row)": 2,
    "Large (1 per row)": 1
}
layout = st.selectbox("Choose Layout Size", list(layout_map.keys()))
num_per_row = layout_map.get(layout, 1)

# A4 setup
margin = 10
a4_width, a4_height = A4
total_margin_space = (num_per_row + 1) * margin
target_width = int((a4_width - total_margin_space) / num_per_row)

# Image preview with remove buttons
if st.session_state.selected_files:
    st.markdown("### Image Previews")
    cols = st.columns(num_per_row)
    to_remove = []

    for i, file in enumerate(st.session_state.selected_files):
        with cols[i % num_per_row]:
            img = Image.open(file)
            st.image(img, use_container_width=True)
            remove_key = f"remove_{i}"
            if st.button("❌", key=remove_key):
                to_remove.append(file)

    # Remove clicked images
    for file in to_remove:
        st.session_state.selected_files.remove(file)

# PDF Generation
if st.button("Generate PDF"):
    if st.session_state.selected_files:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        x_offset = margin
        y_offset = a4_height - margin

        # Sort images by height (aspect ratio)
        def get_img_height(file):
            img = Image.open(file)
            return img.height / img.width
        
        sorted_files = sorted(st.session_state.selected_files, key=get_img_height)

        for uploaded_file in sorted_files:
            image = Image.open(uploaded_file)
            if image.mode != "RGB":
                image = image.convert("RGB")

            aspect_ratio = image.height / image.width
            img_width = target_width
            img_height = int(img_width * aspect_ratio)

            if x_offset + img_width > a4_width - margin:
                x_offset = margin
                y_offset -= img_height + margin

            if y_offset - img_height < margin:
                c.showPage()
                y_offset = a4_height - margin

            c.drawImage(ImageReader(image), x_offset, y_offset - img_height, width=img_width, height=img_height)
            x_offset += img_width + margin

        c.save()
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()

        # PDF Preview
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        st.markdown("### PDF Preview")
        pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

        # Download
        st.download_button("⬇ Download PDF", data=pdf_bytes, file_name="output.pdf", mime="application/pdf")
    else:
        st.warning("Please upload images to generate the PDF.")

# Footer
st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; font-size: 15px; opacity: 0.7;'>Made by HB with Streamlit</div>", unsafe_allow_html=True)
