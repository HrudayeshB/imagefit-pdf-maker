import streamlit as st
from PIL import Image
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import base64
from pdf2image import convert_from_bytes  # ✅ Added for live PDF preview

# Page config
st.set_page_config(page_title="ImageFit PDF Maker", layout="centered")

# Custom CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inject JavaScript
with open("script.js") as js_file:
    js_code = js_file.read()
st.markdown(f"<script>{js_code}</script>", unsafe_allow_html=True)

# Title and Tagline
st.markdown("<div style='text-align: center; font-size: 42px; font-weight: bold'>ImageFit PDF Maker</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; font-size: 16px; opacity: 0.7;'>Fit images. Save paper.</div>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

layout_map = {
    "Very Small (4 per row)": 4,
    "Small (3 per row)": 3,
    "Medium (2 per row)": 2,
    "Large (1 per row)": 1
}
layout = st.selectbox("Choose Layout Size", list(layout_map.keys()), index=2)
num_per_row = layout_map.get(layout, 1)

manual_resize = st.checkbox("Manually enter image width and height?")
custom_width = None
custom_height = None

if manual_resize:
    custom_width = st.number_input("Custom Image Width (px)", min_value=100, max_value=1000, value=300, step=10)
    custom_height = st.number_input("Custom Image Height (px)", min_value=100, max_value=1200, value=400, step=10)

auto_rotate = st.checkbox("Auto-rotate tall images to fit landscape", value=True)

# A4 setup
margin = 10
a4_width, a4_height = A4
target_width = int((a4_width - (num_per_row + 1) * margin) / num_per_row)

# Preview
if uploaded_files and num_per_row > 0:
    st.markdown("### Image Previews")
    cols = st.columns(num_per_row)
    for i, file in enumerate(uploaded_files):
        img = Image.open(file)
        cols[i % num_per_row].image(img, use_container_width=True)

# PDF Generation
if st.button("Generate PDF"):
    if uploaded_files:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        # Preprocess: Convert, Rotate, Resize, Sort
        processed_images = []
        for file in uploaded_files:
            img = Image.open(file)
            if img.mode != "RGB":
                img = img.convert("RGB")
            if auto_rotate and img.height > img.width:
                img = img.rotate(90, expand=True)

            if manual_resize and custom_width and custom_height:
                img_width = custom_width
                img_height = custom_height
            else:
                aspect_ratio = img.height / img.width
                img_width = target_width
                img_height = int(img_width * aspect_ratio)

            processed_images.append((img, img_width, img_height))

        # Sort images by height (shortest first)
        processed_images.sort(key=lambda x: x[2])

        # Dynamic column-wise fill
        x_positions = [margin + i * (target_width + margin) for i in range(num_per_row)]
        y_positions = [a4_height - margin] * num_per_row

        for img, width, height in processed_images:
            # Pick column with highest y-position (most space left)
            col = y_positions.index(max(y_positions))
            x = x_positions[col]
            y = y_positions[col] - height

            # Start new page if overflow
            if y < margin:
                c.showPage()
                y_positions = [a4_height - margin] * num_per_row
                y = y_positions[col] - height

            c.drawImage(ImageReader(img), x, y, width=width, height=height)
            y_positions[col] = y - margin

        c.save()
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()

        # Modern PDF Preview using images
        st.markdown("### PDF Preview")
        preview_images = convert_from_bytes(pdf_bytes, dpi=150)
        for img in preview_images:
            st.image(img, use_container_width=True)

        # Download Button
        st.download_button("⬇ Download PDF", data=pdf_bytes, file_name="output.pdf", mime="application/pdf")
    else:
        st.warning("Please upload images to generate the PDF.")

# Footer
st.markdown("<hr style='border: 1px solid red;'>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; font-size: 15px; opacity: 0.7;'>Made by HB with Streamlit</div>", unsafe_allow_html=True)
