import streamlit as st
import requests
import urllib.request
import os
import datetime
import re
from bs4 import BeautifulSoup
from PIL import Image
from PyPDF2 import PdfReader, PdfMerger
import tempfile

def get_all_images_from_page(page_url):
    """Extract main image URL from a single page"""
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_image = soup.find("img", {"class":"w-100 sky epaper_page"})
        return main_image.get('src') if main_image else None
    except Exception as e:
        st.error(f"Error extracting image from page: {str(e)}")
        return None

def process_newspaper(date=None):
    if date is None:
        date = datetime.datetime.today()

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Scraping Page Links
            html = f"https://epaper.gujaratsamachar.com/ahmedabad/{date.strftime('%d-%m-%Y')}/1"
            r = requests.get(html)
            status_text.write("Website connected successfully")
            progress_bar.progress(20)

            soup = BeautifulSoup(r.content, 'html.parser')
            pages = soup.find("ul", {"class": "nav nav-tabs nav-dots border-bottom-0"})
            page_links = [page['href'] for page in pages.find_all("a", {"class":"anchor_click"}, href=True)]

            # Process each page
            merger = PdfMerger()
            for page_num, page_url in enumerate(page_links, 1):
                # Get main image from the page
                img_url = get_all_images_from_page(page_url)
                if img_url:
                    # Download image to temporary file
                    temp_img_path = os.path.join(temp_dir, f"page_{page_num:02d}.jpg")
                    urllib.request.urlretrieve(img_url, temp_img_path)
                    
                    # Convert image to PDF
                    temp_pdf_path = os.path.join(temp_dir, f"page_{page_num:02d}.pdf")
                    fimg = Image.open(temp_img_path)
                    a4img = Image.new("RGB", (2800, 3974), (255, 255, 255))
                    a4img.paste(fimg, fimg.getbbox())
                    a4img.save(temp_pdf_path, "PDF", quality=70)
                    
                    # Add to merger
                    merger.append(PdfReader(temp_pdf_path, 'rb'))
                
                progress_bar.progress(20 + (70 * page_num // len(page_links)))
                status_text.write(f"Processing page {page_num}/{len(page_links)}")

            # Create final PDF
            final_pdf_path = os.path.join(temp_dir, f"Gujarat_Samachar_{date.strftime('%d-%m-%Y')}.pdf")
            merger.write(final_pdf_path)
            status_text.write("PDF created successfully!")
            progress_bar.progress(100)

            # Read PDF bytes
            with open(final_pdf_path, 'rb') as pdf_file:
                return pdf_file.read()

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

def main():
    st.title("Gujarat Samachar E-Paper Downloader")

    selected_date = st.date_input(
        "Select Date",
        datetime.datetime.today(),
        min_value=datetime.datetime.today() - datetime.timedelta(days=30),
        max_value=datetime.datetime.today()
    )

    if st.button("Download E-Paper"):
        with st.spinner("Processing..."):
            pdf_bytes = process_newspaper(selected_date)
            if pdf_bytes is not None:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"Gujarat_Samachar_{selected_date.strftime('%d-%m-%Y')}.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
# - Temporary files in system temp directory that are automatically cleaned up
# - Final PDF file for download
