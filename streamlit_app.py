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
          os.mkdir(name)
      except FileExistsError:
          st.write(f"Folder {name} already exists")

def download_image(url, file_path, file_name):
  full_path = file_path + file_name + '.jpg'
  urllib.request.urlretrieve(url, full_path)

def process_newspaper(date=None):
  if date is None:
      date = datetime.datetime.today()

  # Create progress bar
  progress_bar = st.progress(0)
  status_text = st.empty()

  # Create temporary directories
  with tempfile.TemporaryDirectory() as temp_dir:
      images_dir = os.path.join(temp_dir, 'images')
      pdfs_dir = os.path.join(temp_dir, 'PDFs')
      os.makedirs(images_dir)
      os.makedirs(pdfs_dir)

      # Scraping Page Links
      html = f"https://epaper.gujaratsamachar.com/ahmedabad/{date.strftime('%d-%m-%Y')}/1"
      try:
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
          for i, url in enumerate(img):
              file_name = f"{i+1:02d}"
              download_image(url, file_path=f"{images_dir}/", file_name=file_name)
          status_text.write("All pages downloaded as images")
          progress_bar.progress(50)

          # Converting Images to PDF
          image_list = os.listdir(images_dir)
          for image in image_list:
              fimg = Image.open(os.path.join(images_dir, image))
              a4img = Image.new("RGB", (2800, 3974), (255, 255, 255))
              a4img.paste(fimg, fimg.getbbox())
              a4img.save(os.path.join(pdfs_dir, f"{image}.pdf"), "PDF", quality=70)
          status_text.write("All images converted to PDF format")
          progress_bar.progress(70)

          # Merging PDFs
          pdfs = os.listdir(pdfs_dir)
          pdfs.sort(key=lambda f: int(re.sub('\D', '', f)))
          merger = PdfMerger()
          for pdf in pdfs:
              merger.append(PdfReader(os.path.join(pdfs_dir, pdf), 'rb'))

          final_pdf_path = f"Gujarat Samachar_{date.strftime('%d-%m-%Y')}.pdf"
          merger.write(final_pdf_path)
          status_text.write("PDF created successfully!")
          progress_bar.progress(100)

          # Return the final PDF for download
          with open(final_pdf_path, 'rb') as pdf_file:
              pdf_bytes = pdf_file.read()
          return pdf_bytes

      except Exception as e:
          st.error(f"An error occurred: {str(e)}")
          return None

def main():
  st.title("Gujarat Samachar E-Paper Downloader")
  st.write("Download Gujarat Samachar e-paper as PDF")

  # Date selection
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
