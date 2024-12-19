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

def process_newspaper(date=None):
    if date is None:
        date = datetime.datetime.today()

    # Create progress bar
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
        listofPage = []
        for page in pages.find_all("a", {"class":"anchor_click"}, href=True):
            listofPage.append(page['href'])

        # Scraping Image Links
        img = []
        for pages in listofPage:
            p = BeautifulSoup(requests.get(pages).content, 'html.parser')
            s = p.find("img", {"class":"w-100 sky epaper_page"})
            img.append(s.get('src'))
        status_text.write("Page links scraped successfully")
        progress_bar.progress(30)

        # Downloading Images
        downloaded_images = []
        for i, url in enumerate(img):
            file_name = f"page_{i+1:02d}"
            image_path = download_image(url, date_folder, file_name)
            if image_path:
                downloaded_images.append(image_path)
                status_text.write(f"Downloaded page {i+1}")
        status_text.write(f"All {len(downloaded_images)} pages downloaded as images")
        progress_bar.progress(50)

        # Converting Images to PDF
        pdf_folder = 'PDFs'
        os.makedirs(pdf_folder, exist_ok=True)

        for image_path in downloaded_images:
            pdf_name = os.path.basename(image_path).replace('.jpg', '.pdf')
            fimg = Image.open(image_path)
            a4img = Image.new("RGB", (2800, 3974), (255, 255, 255))
            a4img.paste(fimg, fimg.getbbox())
            a4img.save(os.path.join(pdf_folder, pdf_name), "PDF", quality=70)
        status_text.write("All images converted to PDF format")
        progress_bar.progress(70)

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

        # Return both PDF bytes and the path to downloaded images
        return pdf_bytes, date_folder

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None, None

def main():
    st.title("Gujarat Samachar E-Paper Downloader")
    st.write("Download Gujarat Samachar e-paper as PDF and Images")

    # Date selection
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
                    images = sorted([f for f in os.listdir(images_folder) if f.endswith('.jpg')])
                    for image in images:
                        img_path = os.path.join(images_folder, image)
                        st.image(img_path, caption=f"Page {image.split('_')[1].split('.')[0]}")

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
# - images/{date}/page_XX.jpg (multiple image files)
# - PDFs/page_XX.pdf (multiple PDF files)
# - Gujarat Samachar_{date}.pdf (final merged PDF)
