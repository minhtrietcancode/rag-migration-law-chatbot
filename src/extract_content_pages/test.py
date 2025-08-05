
import os
from PyPDF2 import PdfReader
from clean_content_page import clean_extracted_text

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
    page_num = 28
    text = extract_text_from_pdf(rel_path, page_num)
    cleaned_text = clean_extracted_text(text) if text else "[No text extracted]"
    # Create output filename based on PDF name and page number
    pdf_name = os.path.splitext(os.path.basename(rel_path))[0]
    output_filename = f"{pdf_name}_page_{page_num}_cleaned.txt"
    output_path = os.path.join(os.path.dirname(rel_path), output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)
    print(f"Cleaned extracted text saved to {output_path}")
