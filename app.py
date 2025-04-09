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

# Custom CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inject JavaScript
with open("script.js") as js_file:
    js_code = js_file.read()
st.markdown(f"<script>{js_code}</script>", unsafe_allow_html=True)

# Title
st.markdown("<h1>ImageFit PDF Maker</h1>", unsafe_allow_html=True)
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

st.markdown("Optional: Manual Resize")
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
total_margin_space = (num_per_row + 1) * margin
target_width = int((a4_width - total_margin_space) / num_per_row)

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

        processed_images = []

        for uploaded_file in uploaded_files:
            img = Image.open(uploaded_file)
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

        # Sort tall images to the end
        processed_images.sort(key=lambda x: x[2])  # sort by height

        # Group images by similar height to reduce vertical gaps
        grouped_rows = []
        row = []
        row_heights = []
        for img, w, h in processed_images:
            row.append((img, w, h))
            row_heights.append(h)
            if len(row) == num_per_row:
                grouped_rows.append((row.copy(), max(row_heights)))
                row = []
                row_heights = []
        if row:
            grouped_rows.append((row, max(row_heights)))

        # Start placing rows
        y_offset = a4_height - margin
        for row_imgs, row_height in grouped_rows:
            x_offset = margin
            if y_offset - row_height < margin:
                c.showPage()
                y_offset = a4_height - margin
            for img, w, h in row_imgs:
                y_pos = y_offset - h  # align bottom
                c.drawImage(ImageReader(img), x_offset, y_pos, width=w, height=h)
                x_offset += w + margin
            y_offset -= row_height + margin

        c.save()
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()

        # Preview
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
