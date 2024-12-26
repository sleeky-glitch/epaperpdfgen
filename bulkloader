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
import calendar

def get_all_images_from_page(page_url):
    """Extract main image URL from a single page"""
    try:
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_image = soup.find("img", {"class":"w-100 sky epaper_page"})
        return main_image.get('src') if main_image else None
    except Exception as e:
        return None

def process_newspaper(date, progress_bar, status_text):
    """Process single newspaper for a given date"""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Scraping Page Links
            html = f"https://epaper.gujaratsamachar.com/ahmedabad/{date.strftime('%d-%m-%Y')}/1"
            r = requests.get(html)
            if r.status_code != 200:
                status_text.write(f"No paper available for {date.strftime('%d-%m-%Y')}")
                return None
            
            progress_bar.progress(20)
            soup = BeautifulSoup(r.content, 'html.parser')
            pages = soup.find("ul", {"class": "nav nav-tabs nav-dots border-bottom-0"})
            if not pages:
                status_text.write(f"No pages found for {date.strftime('%d-%m-%Y')}")
                return None
                
            page_links = [page['href'] for page in pages.find_all("a", {"class":"anchor_click"}, href=True)]

            # Process each page
            merger = PdfMerger()
            for page_num, page_url in enumerate(page_links, 1):
                img_url = get_all_images_from_page(page_url)
                if img_url:
                    # Download and process image
                    temp_img_path = os.path.join(temp_dir, f"page_{page_num:02d}.jpg")
                    urllib.request.urlretrieve(img_url, temp_img_path)

                    temp_pdf_path = os.path.join(temp_dir, f"page_{page_num:02d}.pdf")
                    fimg = Image.open(temp_img_path)
                    a4img = Image.new("RGB", (2800, 3974), (255, 255, 255))
                    a4img.paste(fimg, fimg.getbbox())
                    a4img.save(temp_pdf_path, "PDF", quality=70)

                    merger.append(PdfReader(temp_pdf_path, 'rb'))

                progress_bar.progress(20 + (70 * page_num // len(page_links)))
                status_text.write(f"Processing page {page_num}/{len(page_links)}")

            # Create final PDF
            final_pdf_path = os.path.join(temp_dir, f"Gujarat_Samachar_{date.strftime('%d-%m-%Y')}.pdf")
            merger.write(final_pdf_path)
            progress_bar.progress(100)
            status_text.write("Ready for download!")

            with open(final_pdf_path, 'rb') as pdf_file:
                return pdf_file.read()

        except Exception as e:
            status_text.write(f"Error: {str(e)}")
            return None

def main():
    st.title("Gujarat Samachar E-Paper Monthly Downloader")

    # Month and year selection
    current_date = datetime.datetime.today()
    selected_month = st.selectbox(
        "Select Month",
        range(1, 13),
        index=current_date.month - 1
    )
    selected_year = st.selectbox(
        "Select Year",
        range(current_date.year - 1, current_date.year + 1),
        index=1
    )

    if st.button("Load Papers for Selected Month"):
        # Get number of days in selected month
        num_days = calendar.monthrange(selected_year, selected_month)[1]
        
        # Create a container for all papers
        papers_container = st.container()
        
        with papers_container:
            for day in range(1, num_days + 1):
                try:
                    date = datetime.datetime(selected_year, selected_month, day)
                    
                    # Skip future dates
                    if date > current_date:
                        continue
                    
                    # Create columns for each paper
                    col1, col2, col3 = st.columns([2, 6, 2])
                    
                    with col1:
                        st.write(date.strftime('%d-%m-%Y'))
                    
                    with col2:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                    
                    with col3:
                        # Create unique keys for each date's components
                        pdf_key = f"pdf_{date.strftime('%d-%m-%Y')}"
                        if pdf_key not in st.session_state:
                            st.session_state[pdf_key] = process_newspaper(date, progress_bar, status_text)
                        
                        if st.session_state[pdf_key] is not None:
                            st.download_button(
                                label="Download",
                                data=st.session_state[pdf_key],
                                file_name=f"Gujarat_Samachar_{date.strftime('%d-%m-%Y')}.pdf",
                                mime="application/pdf",
                                key=f"download_{date.strftime('%d-%m-%Y')}"
                            )
                    
                    st.divider()
                    
                except Exception as e:
                    st.error(f"Error processing {date.strftime('%d-%m-%Y')}: {str(e)}")

if __name__ == "__main__":
    main()

# Created/Modified files during execution:
# - Temporary files in system temp directory that are automatically cleaned up
# - PDFs available for download through Streamlit's download button
