# mini-OCR_v2
This project contains an OCR (Optical Character Recognition) script designed to process and extract text from documents, with a focus on forms like with a mix of typed and handwritten text written in German. The script leverages advanced image processing and OCR technologies to handle document segmentation, text extraction, and identifier parsing, making it a valuable tool for digitizing handwritten and printed records.

## Project Overview
### Purpose
The primary goal is to automate the extraction of structured data (e.g., section titles, lists, and identifiers like `ID:` and `Rev.-Index:`) from scanned documents, for other digital usage of the data.

### Current Features
- Image Preprocessing: Includes grayscale conversion and an experimental deskewing function to correct image rotation using contour detection.
- Section Splitting: Divides the document into three horizontal sections: header, main content, and footer, with adjustable boundaries based on image height.
- Column Segmentation: Splits the main content into three columns with custom widths (48% left, 19% middle, 33% right) to reflect uneven content distribution.
- Text Extraction: Uses EasyOCR for initial text detection and Tesseract OCR for refining handwritten sections, with output organized by section and column.
- Export Functionality: Saves processed image sections (header, footer, main content, and columns) as PNG files in a `temp/` directory for review.
- Identifier Extraction: Captures document identifiers (e.g., `ID: 55358`, `Rev.-Index: 000/11.2014`) from footer text.

## Current Status
- The script is in an early development stage, with initial functionality implemented and tested on sample images (e.g., `images/MDS-UPDRS_page-0001.png`).
- Deskewing and rotation correction are partially functional but require further refinement, as the current logic often detects a 0.00-degree angle.
- Preprocessing steps (e.g., contrast enhancement, thresholding, denoising) are commented out, you can uncomment them to tweak OCR accuracy.
- Handwritten text recognition (e.g., in middle and right columns) needs improvement, with Tesseract integration ongoing.

## Installation
### Prerequisites
- Python 3.x
- EasyOCR
- Tesseract

### Dependencies
Install packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```
If installation from the `requirement.txt` doesn't work, you can manually install:
```bash
pip install easyocr opencv-python numpy pillow pytesseract
```
### Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/Shetteemah/mini-OCR_v2.git
    ```
    ```bash
    cd mini-OCR_v2
    ```
2. Place your input image (e.g., `MDS-UPDRS_page-0001.png`) in the `images/` directory. (Note: If `images/` is excluded via `.gitignore`, create it manually and add your image.)
3. Ensure Tesseract OCR is installed on your system:
- On Ubuntu: `sudo apt install tesseract-ocr`
- On macOS: `brew install tesseract`
- On Windows: Download and install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage
### Running the Script
Execute the script with:
```bash
python ocr_script.py
```

### Output
- Terminal: Displays extracted text for the header, left column, middle column, right column, and document identifiers (`ID:` and `Rev.-Index:`).
- temp/: Contains exported PNG images
    - `preprocessed_image.png`
    - `header.png`
    - `footer.png`
    - `main_content.png`
    - `left_column.png`
    - `middle_column.png`
    - `right_column.png`

### Example Input
- Input image: `images/MDS-UPDRS_page-0001.png`

### Example Output
- Header Text: e.g., "MDS-UPDRS", "Datum:", "L-Dopa Dosis:"
- Left Column Text: e.g., "Teil A Komplexes Verhalten...", "1.1 Kognitive Beeinträchtigung..."
- Middle Column Text: e.g., "Med ON" with handwritten scores
- Right Column Text: e.g., "Med OFF" with handwritten scores
- Document ID: e.g., "55358"
- Revision Index: e.g., "000/11.2014"

### Future Development
- Ability to section based on form (UPDRS or MDS-UPDRS) and page (page 1 or page 2)
- Re-enable and optimize image preprocessing (e.g., `equalizeHist`, `adaptiveThreshold`, `fastNlMeansDenoising`).
- Fix deskewing logic with alternative methods (e.g., Hough Line Transform) to handle tilts (e.g., ~2-3 degrees).
- Integrate Tesseract results with EasyOCR for a hybrid approach to improve accuracy.
- Add post-processing to clean OCR output (e.g., correcting misreadings like "Schrerz" to "Schmerz").
- Explore custom Tesseract models for better handwritten text recognition.

### License
You can find the license [here](LICENSE).