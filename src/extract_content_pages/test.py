import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_relative_path, page_number):
    """
    Extract text from a specific page of a PDF file.
    Args:
        pdf_relative_path (str): Relative path to the PDF file.
        page_number (int): 1-based page number to extract.
    Returns:
        str: Extracted text from the specified page.
    """
    # Convert to absolute path
    pdf_path = os.path.abspath(pdf_relative_path)
    reader = PdfReader(pdf_path)
    # PyPDF2 uses 0-based indexing for pages
    if page_number < 1 or page_number > len(reader.pages):
        raise ValueError(f"Page number {page_number} is out of range. PDF has {len(reader.pages)} pages.")
    page = reader.pages[page_number - 1]
    return page.extract_text()

# Example usage:
if __name__ == "__main__":
    rel_path = "Migration Act 1958/Migration Act 1958 – Volume 1.pdf"
    page_num = 27
    text = extract_text_from_pdf(rel_path, page_num)
    print(text)
