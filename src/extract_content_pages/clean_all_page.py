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
