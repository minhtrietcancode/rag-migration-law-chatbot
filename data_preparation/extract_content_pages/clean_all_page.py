# import the function for extracting the page --> cleaning the extracted page
from extract_content_page import extract_text_from_pdf
from clean_content_page import clean_extracted_text

# Volume 1 Start Page in Pdf / Actual 
VOLUME_1_PDF_START_CONTENT_PAGE = 1
VOLUME_1_REAL_START_CONTENT_PAGE = 27

# Volume 1 End Page in Pdf / Actual 
VOLUME_1_PDF_END_CONTENT_PAGE = 537
VOLUME_1_REAL_END_CONTENT_PAGE = 563

# Volume 2 Start Page in Pdf / Actual 
VOLUME_2_PDF_START_CONTENT_PAGE = 1
VOLUME_2_REAL_START_CONTENT_PAGE = 19

# Volume 2 End Page in Pdf / Actual 
VOLUME_2_PDF_END_CONTENT_PAGE = 311
VOLUME_2_REAL_END_CONTENT_PAGE = 329

# Gap between pdf and actual page for 2 volumes
VOLUME_1_PDF_REAL_PAGE_GAP = 26
VOLUME_2_PDF_REAL_PAGE_GAP = 18

# Relative path that the generated .txt files should be saved
VOLUME_1_CONTENT_PAGE_TXT_FORMAT_PATH = 'Migration Act Content Pages Txt Format/volume 1'
VOLUME_2_CONTENT_PAGE_TXT_FORMAT_PATH = 'Migration Act Content Pages Txt Format/volume 2'

# import os for directory creation and file saving
import os

def extract_clean_save_pages(pdf_path, start_page, end_page, output_dir, page_gap_real_pdf):
    """
    Extracts, cleans, and saves each page in the given range from the PDF.
    Args:
        pdf_path (str): Path to the PDF file.
        start_page (int): 1-based start page (inclusive).
        end_page (int): 1-based end page (inclusive).
        output_dir (str): Directory to save the cleaned .txt files.
    """
    os.makedirs(output_dir, exist_ok=True)
    for page_num in range(start_page, end_page + 1):
        try:
            text = extract_text_from_pdf(pdf_path, page_num)
            cleaned = clean_extracted_text(text) if text else "[No text extracted]"
            output_filename = f"page_{page_num - page_gap_real_pdf}.txt"
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"Saved cleaned page {page_num - page_gap_real_pdf} to {output_path}")
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")

# Call the function
VOLUME_1_PDF_PATH = "Migration Act 1958/Migration Act 1958 – Volume 1.pdf"
VOLUME_2_PDF_PATH = "Migration Act 1958/Migration Act 1958 – Volume 2.pdf"
extract_clean_save_pages(VOLUME_1_PDF_PATH, VOLUME_1_REAL_START_CONTENT_PAGE, 
                         VOLUME_1_REAL_END_CONTENT_PAGE, VOLUME_1_CONTENT_PAGE_TXT_FORMAT_PATH,
                         VOLUME_1_PDF_REAL_PAGE_GAP)
extract_clean_save_pages(VOLUME_2_PDF_PATH, VOLUME_2_REAL_START_CONTENT_PAGE, 
                         VOLUME_2_REAL_END_CONTENT_PAGE, VOLUME_2_CONTENT_PAGE_TXT_FORMAT_PATH,
                         VOLUME_2_PDF_REAL_PAGE_GAP)
