# Gujarat Samachar E-Paper Downloader

A Streamlit web application that allows users to download the Gujarat Samachar e-paper as a PDF file. The application scrapes the official e-paper website, processes the pages, and generates a downloadable PDF.

## Features

- **Date Selection**: Choose any date within the last 30 days
- **Automated Processing**: Automatically scrapes, downloads, and converts newspaper pages
- **Progress Tracking**: Real-time progress updates with status messages
- **PDF Generation**: Creates a high-quality, merged PDF of all newspaper pages
- **Easy Download**: Simple one-click download of the generated PDF

## Prerequisites

Required packages:
- streamlit
- requests
- beautifulsoup4
- Pillow
- PyPDF2
- urllib3

## Installation

1. Clone the repository:

bash
git clone https://github.com/yourusername/gujarat-samachar-downloader.git
cd gujarat-samachar-downloader

2. Install dependencies:

bash
pip install -r requirements.txt

3. Run the application:

bash
streamlit run app.py

## Usage

1. Launch the application using the command above
2. Select a date using the date picker (limited to the last 30 days)
3. Click the "Download E-Paper" button
4. Wait for the processing to complete
5. Click "Download PDF" to save the newspaper

## How It Works

The application follows these steps:
1. Creates temporary directories for processing
2. Scrapes the e-paper website for page links
3. Downloads individual page images
4. Converts images to PDF format
5. Merges all PDFs into a single file
6. Provides the final PDF for download

## Technical Details

### Main Components

- `create_folders()`: Creates necessary directories
- `download_image()`: Handles image downloads
- `process_newspaper()`: Main processing pipeline
- `main()`: Streamlit interface and user interaction

### Image Processing

- Images are standardized to A4 size (2800 x 3974 pixels)
- Conversion to PDF maintains 70% quality for optimal file size
- Pages are automatically ordered correctly in the final PDF

## Error Handling

- Graceful handling of network errors
- Directory creation error management
- Process status updates
- User-friendly error messages

## Limitations

- Can only download papers from the last 30 days
- Requires stable internet connection
- Processing time depends on number of pages and internet speed

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

- Gujarat Samachar for providing the e-paper service
- Streamlit for the wonderful web framework
- All contributors and users of this application

## Support

For support, please open an issue in the GitHub repository or contact nishanttomar98@gmail.com

---

**Note**: This application is for personal use only. Please respect Gujarat Samachar's terms of service and copyright policie
