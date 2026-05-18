import io
import re

import img2pdf
import markdown
import streamlit as st
from PIL import Image
from xhtml2pdf import pisa


st.set_page_config(
    page_title="File to PDF Converter",
    page_icon="📄",
    layout="centered",
)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <style>
        @page {
            size: A4;
            margin: 24mm 18mm;
        }
        body {
            font-family: Helvetica, Arial, sans-serif;
            color: #1f2937;
            font-size: 11pt;
            line-height: 1.6;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #111827;
            margin-top: 18px;
            margin-bottom: 8px;
            line-height: 1.25;
        }
        h1 { font-size: 24pt; }
        h2 { font-size: 18pt; }
        h3 { font-size: 14pt; }
        p, ul, ol {
            margin-bottom: 10px;
        }
        code {
            font-family: Courier, monospace;
            background: #f3f4f6;
            padding: 2px 4px;
        }
        pre {
            background: #f3f4f6;
            border: 1px solid #e5e7eb;
            padding: 10px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        blockquote {
            border-left: 4px solid #d1d5db;
            color: #4b5563;
            margin: 12px 0;
            padding-left: 12px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
        }
        th, td {
            border: 1px solid #d1d5db;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background: #f9fafb;
        }
        a {
            color: #2563eb;
            text-decoration: none;
        }
        hr {
            border: none;
            border-top: 1px solid #d1d5db;
            margin: 16px 0;
        }
    </style>
</head>
<body>
{body}
</body>
</html>
"""


def sanitize_filename(name: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", (name or "").strip())
    cleaned = cleaned.strip("._")
    return cleaned or fallback



def read_uploaded_text(uploaded_file) -> str:
    raw = uploaded_file.getvalue()
    for encoding in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")



def convert_images_to_pdf(uploaded_files):
    image_bytes_list = []
    for uploaded_file in uploaded_files:
        uploaded_file.seek(0)
        image_bytes_list.append(uploaded_file.read())
    return img2pdf.convert(image_bytes_list)



def convert_markdown_to_pdf(markdown_text: str):
    html_body = markdown.markdown(
        markdown_text,
        extensions=["extra", "tables", "fenced_code", "sane_lists", "toc"],
    )
    html_document = HTML_TEMPLATE.format(body=html_body)
    output = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html_document), dest=output)
    return output.getvalue(), pdf.err


st.title("📄 File to PDF Converter")
st.markdown(
    "Convert **images** or **Markdown** files into downloadable PDF documents."
)

image_tab, markdown_tab = st.tabs(["🖼️ Image to PDF", "📝 Markdown to PDF"])

with image_tab:
    st.subheader("Image to PDF")
    st.write("Upload one or more JPG, PNG, or WebP files and combine them into a single PDF.")

    uploaded_images = st.file_uploader(
        "Choose image files",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        help="Select one or more image files to convert to a single PDF.",
        key="image_uploader",
    )

    if uploaded_images:
        st.success(f"✓ {len(uploaded_images)} file(s) uploaded")
        st.subheader("Preview")

        cols_per_row = 3
        for i in range(0, len(uploaded_images), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(uploaded_images):
                    with col:
                        file = uploaded_images[i + j]
                        image = Image.open(file)
                        st.image(image, caption=file.name, use_container_width=True)
                        file.seek(0)

        image_pdf_filename = st.text_input(
            "Output filename (without extension)",
            value="converted_images",
            key="image_filename",
        )

        if st.button("🔄 Convert images to PDF", type="primary", key="image_convert"):
            try:
                with st.spinner("Converting images to PDF..."):
                    pdf_bytes = convert_images_to_pdf(uploaded_images)

                final_name = sanitize_filename(image_pdf_filename, "converted_images")
                st.success("✓ PDF created successfully!")
                st.download_button(
                    label="📥 Download image PDF",
                    data=pdf_bytes,
                    file_name=f"{final_name}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key="image_download",
                )

                pdf_size_mb = len(pdf_bytes) / (1024 * 1024)
                st.info(f"📊 PDF size: {pdf_size_mb:.2f} MB | Pages: {len(uploaded_images)}")
            except Exception as exc:
                st.error(f"❌ Error converting images to PDF: {exc}")
                st.exception(exc)
    else:
        st.info("👆 Upload image files to get started")

with markdown_tab:
    st.subheader("Markdown to PDF")
    st.write("Upload a Markdown file, preview it, and export it as a styled PDF document.")

    uploaded_markdown = st.file_uploader(
        "Choose a Markdown file",
        type=["md", "markdown"],
        accept_multiple_files=False,
        help="Upload a .md or .markdown file.",
        key="markdown_uploader",
    )

    if uploaded_markdown is not None:
        markdown_text = read_uploaded_text(uploaded_markdown)
        default_name = sanitize_filename(uploaded_markdown.name.rsplit('.', 1)[0], "converted_markdown")

        st.success(f"✓ Uploaded: {uploaded_markdown.name}")
        markdown_pdf_filename = st.text_input(
            "Output filename (without extension)",
            value=default_name,
            key="markdown_filename",
        )

        st.subheader("Preview")
        st.markdown(markdown_text)

        with st.expander("Show raw Markdown"):
            st.code(markdown_text, language="markdown")

        if st.button("🔄 Convert Markdown to PDF", type="primary", key="markdown_convert"):
            try:
                with st.spinner("Converting Markdown to PDF..."):
                    pdf_bytes, pdf_error = convert_markdown_to_pdf(markdown_text)

                if pdf_error:
                    raise ValueError("The PDF renderer could not process the Markdown content.")

                final_name = sanitize_filename(markdown_pdf_filename, "converted_markdown")
                st.success("✓ PDF created successfully!")
                st.download_button(
                    label="📥 Download Markdown PDF",
                    data=pdf_bytes,
                    file_name=f"{final_name}.pdf",
                    mime="application/pdf",
                    type="primary",
                    key="markdown_download",
                )

                pdf_size_kb = len(pdf_bytes) / 1024
                st.info(f"📊 PDF size: {pdf_size_kb:.1f} KB")
            except Exception as exc:
                st.error(f"❌ Error converting Markdown to PDF: {exc}")
                st.exception(exc)
    else:
        st.info("👆 Upload a Markdown file to get started")

with st.expander("ℹ️ Features"):
    st.markdown(
        """
- Image mode supports JPG, JPEG, PNG, and WebP.
- Markdown mode supports headings, lists, tables, blockquotes, links, and fenced code blocks.
- PDF files are generated in memory and downloaded directly from the app.
        """
    )

st.markdown("---")
st.caption("Built with Streamlit, img2pdf, markdown, and xhtml2pdf")
