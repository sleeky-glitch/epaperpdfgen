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

def create_folders():
    dir_names = ['images/', 'PDFs/']
    for name in dir_names:
        try:
            os.makedirs(name, exist_ok=True)
        except Exception as e:
            st.write(f"Error creating folder {name}: {str(e)}")

def download_image(url, file_path, file_name):
    try:
        full_path = os.path.join(file_path, f"{file_name}.jpg")
        urllib.request.urlretrieve(url, full_path)
        return full_path
    except Exception as e:
        st.error(f"Error downloading image: {str(e)}")
        return None

def get_all_images_from_page(page_url):
    """Extract all image URLs from a single page"""
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all image elements
        images = []

        # Main e-paper image
        main_image = soup.find("img", {"class":"w-100 sky epaper_page"})
        if main_image and main_image.get('src'):
            images.append(('main', main_image.get('src')))

        # Find all other images on the page
        all_images = soup.find_all("img")
        for idx, img in enumerate(all_images):
            src = img.get('src')
            if src and src.startswith('http') and 'epaper' in src.lower():
                if src not in [img[1] for img in images]:  # Avoid duplicates
                    images.append((f'additional_{idx}', src))

        return images
    except Exception as e:
        st.error(f"Error extracting images from page: {str(e)}")
        return []

def process_newspaper(date=None):
    if date is None:
        date = datetime.datetime.today()

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Create folders for storing images and PDFs
    create_folders()

    # Create date-specific folder for images
    date_folder = os.path.join('images', date.strftime('%d-%m-%Y'))
    os.makedirs(date_folder, exist_ok=True)

    try:
        # Scraping Page Links
        html = f"https://epaper.gujaratsamachar.com/ahmedabad/{date.strftime('%d-%m-%Y')}/1"
        r = requests.get(html)
        status_text.write("Website connected successfully")
        progress_bar.progress(10)

        soup = BeautifulSoup(r.content, 'html.parser')
        pages = soup.find("ul", {"class": "nav nav-tabs nav-dots border-bottom-0"})
        page_links = [page['href'] for page in pages.find_all("a", {"class":"anchor_click"}, href=True)]

        status_text.write("Page links scraped successfully")
        progress_bar.progress(20)

        # Download images from each page
        downloaded_images = []
        for page_num, page_url in enumerate(page_links, 1):
            # Create page-specific folder
            page_folder = os.path.join(date_folder, f'page_{page_num:02d}')
            os.makedirs(page_folder, exist_ok=True)

            # Get all images from the page
            page_images = get_all_images_from_page(page_url)

            status_text.write(f"Found {len(page_images)} images on page {page_num}")

            # Download each image
            for img_type, img_url in page_images:
                file_name = f"page_{page_num:02d}_{img_type}"
                image_path = download_image(img_url, page_folder, file_name)
                if image_path:
                    downloaded_images.append(image_path)
                    status_text.write(f"Downloaded {file_name}")

            progress_bar.progress(20 + (60 * page_num // len(page_links)))

        status_text.write(f"All {len(downloaded_images)} images downloaded")
        progress_bar.progress(80)

        # Converting Images to PDF
        pdf_folder = 'PDFs'
        os.makedirs(pdf_folder, exist_ok=True)

        # Convert main images to PDF
        main_images = [img for img in downloaded_images if 'main' in img]
        for image_path in main_images:
            pdf_name = os.path.basename(image_path).replace('.jpg', '.pdf')
            fimg = Image.open(image_path)
            a4img = Image.new("RGB", (2800, 3974), (255, 255, 255))
            a4img.paste(fimg, fimg.getbbox())
            a4img.save(os.path.join(pdf_folder, pdf_name), "PDF", quality=70)

        status_text.write("All main images converted to PDF format")
        progress_bar.progress(90)

        # Merging PDFs
        pdfs = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        pdfs.sort(key=lambda f: int(re.search(r'\d+', f).group()))
        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(PdfReader(os.path.join(pdf_folder, pdf), 'rb'))

        final_pdf_path = f"Gujarat Samachar_{date.strftime('%d-%m-%Y')}.pdf"
        merger.write(final_pdf_path)
        status_text.write("PDF created successfully!")
        progress_bar.progress(100)

        # Return the final PDF for download
        with open(final_pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()

        return pdf_bytes, date_folder

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, None

def main():
    st.title("Gujarat Samachar E-Paper Downloader")
    st.write("Download Gujarat Samachar e-paper as PDF and Images")

    selected_date = st.date_input(
        "Select Date",
        datetime.datetime.today(),
        min_value=datetime.datetime.today() - datetime.timedelta(days=30),
        max_value=datetime.datetime.today()
    )

    if st.button("Download E-Paper"):
        with st.spinner("Processing..."):
            pdf_bytes, images_folder = process_newspaper(selected_date)
            if pdf_bytes is not None:
                st.download_button(
                    label="Download PDF",
                    data=pdf_bytes,
                    file_name=f"Gujarat_Samachar_{selected_date.strftime('%d-%m-%Y')}.pdf",
                    mime="application/pdf"
                )

                # Display downloaded images
                if images_folder and os.path.exists(images_folder):
                    st.write("Downloaded Images:")
                    # Iterate through page folders
                    page_folders = sorted([f for f in os.listdir(images_folder) if os.path.isdir(os.path.join(images_folder, f))])
                    for page_folder in page_folders:
                        st.write(f"### {page_folder}")
                        page_path = os.path.join(images_folder, page_folder)
                        images = sorted([f for f in os.listdir(page_path) if f.endswith('.jpg')])
                        for image in images:
                            img_path = os.path.join(page_path, image)
                            st.image(img_path, caption=image)

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
# - images/{date}/page_XX/page_XX_main.jpg
# - images/{date}/page_XX/page_XX_additional_Y.jpg
# - PDFs/page_XX.pdf
# - Gujarat Samachar_{date}.pdf
