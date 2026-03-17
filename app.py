import streamlit as st
import img2pdf
import io
from PIL import Image
import os

# Page configuration
st.set_page_config(
    page_title="Image to PDF Converter",
    page_icon="📄",
    layout="centered"
)

# Title and description
st.title("📄 Image to PDF Converter")
st.markdown("""
Upload one or more images (JPG, PNG, WebP) and convert them to a single PDF file.
Uses **img2pdf** for lossless conversion.
""")

# File uploader
uploaded_files = st.file_uploader(
    "Choose image files",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    help="Select one or more image files to convert to PDF"
)

if uploaded_files:
    st.success(f"✓ {len(uploaded_files)} file(s) uploaded")
    
    # Display uploaded images in columns
    st.subheader("Preview")
    
    # Show images in a grid
    cols_per_row = 3
    for i in range(0, len(uploaded_files), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(uploaded_files):
                with col:
                    file = uploaded_files[i + j]
                    # Display image
                    image = Image.open(file)
                    st.image(image, caption=file.name, use_container_width=True)
                    # Reset file pointer
                    file.seek(0)
    
    # PDF filename input
    st.subheader("PDF Settings")
    pdf_filename = st.text_input(
        "Output filename (without extension)",
        value="converted_images",
        help="Enter the name for your PDF file"
    )
    
    # Convert button
    if st.button("🔄 Convert to PDF", type="primary"):
        try:
            # Progress indicator
            with st.spinner("Converting images to PDF..."):
                # Read all uploaded files as bytes
                image_bytes_list = []
                for uploaded_file in uploaded_files:
                    # Reset file pointer to beginning
                    uploaded_file.seek(0)
                    # Read file bytes
                    image_bytes_list.append(uploaded_file.read())
                
                # Convert images to PDF using img2pdf
                pdf_bytes = img2pdf.convert(image_bytes_list)
            
            # Success message
            st.success("✓ PDF created successfully!")
            
            # Download button
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=f"{pdf_filename}.pdf",
                mime="application/pdf",
                type="primary"
            )
            
            # Show file info
            pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
            st.info(f"📊 PDF size: {pdf_size_mb:.2f} MB | Pages: {len(uploaded_files)}")
            
        except Exception as e:
            st.error(f"❌ Error converting to PDF: {str(e)}")
            st.exception(e)

else:
    # Instructions when no files uploaded
    st.info("👆 Upload image files to get started")
    
    # Features section
    with st.expander("ℹ️ Features & Benefits"):
        st.markdown("""
        **Key Features:**
        - 🖼️ Supports JPG, PNG, and WebP formats
        - 📚 Combine multiple images into one PDF
        - 🎯 Lossless conversion (no quality loss)
        - ⚡ Fast processing
        - 📦 Smallest file size (direct embedding)
        - 🔒 Privacy-focused (all processing in browser)
        
        **How to use:**
        1. Click "Browse files" or drag & drop images
        2. Preview your uploaded images
        3. Enter a filename for your PDF (optional)
        4. Click "Convert to PDF"
        5. Download your PDF file
        """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit and img2pdf | No data is stored on the server")
