import streamlit as st
from PIL import Image
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import tempfile
import base64


# Page config
st.set_page_config(page_title="ImageFit PDF Maker", layout="centered")

# Custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inject external JavaScript
with open("script.js") as js_file:
    js_code = js_file.read()

st.markdown(f"<script>{js_code}</script>", unsafe_allow_html=True)


# Title
st.markdown("<h1>ImageFit PDF Maker</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

# Layout selector
layout = st.selectbox("Choose Layout Size", ["Very Small (4 per row)", "Small (3 per row)", "Medium (2 per row)", "Large (1 per row)"])

layout_map = {
    "Very Small (4 per row)": 4,
    "Small (3 per row)": 3,
    "Medium (2 per row)": 2,
    "Large (1 per row)": 1
}

num_per_row = layout_map[layout]

# A4 setup
margin = 10
a4_width, a4_height = A4
total_margin_space = (num_per_row + 1) * margin
target_width = int((a4_width - total_margin_space) / num_per_row)

# # Image Preview
# if uploaded_files:
#     st.markdown("### Image Previews")
#     cols = st.columns(num_per_row)
#     for i, file in enumerate(uploaded_files):
#         img = Image.open(file)
#         aspect_ratio = img.height / img.width
#         resized_img = img.resize((target_width, int(target_width * aspect_ratio)))
#         cols[i % num_per_row].image(resized_img, use_container_width=True)

# Image Preview
if uploaded_files:
    st.markdown("### Images Preview")
    cols = st.columns(num_per_row)
    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        cols[i % num_per_row].image(img, use_container_width=True)


# PDF Generation
if st.button("Generate PDF"):
    if uploaded_files:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        x_offset = margin
        y_offset = a4_height - margin

        for uploaded_file in uploaded_files:
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
        pdf_bytes = buffer.getvalue()  # Get the PDF bytes once

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
st.markdown("<div style='text-align: center; font-size: 15px; opacity: 0.7;'>Made by HB and Streamlit</div>", unsafe_allow_html=True)
