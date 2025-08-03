import PyPDF2
import re

START_INDEX_PAGES = 3
END_INDEX_PAGES = 25

def fix_broken_lines(text):
    """
    Fixes broken lines in the table of contents and removes dot leaders.
    
    :param text: Raw cleaned text with broken lines
    :return: Text with fixed line breaks and removed dot leaders
    """
    lines = text.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        current_line = lines[i].strip()
        
        # Skip empty lines
        if not current_line:
            i += 1
            continue
            
        # Check if this is a table of contents entry (starts with number/letter or is a header)
        if re.match(r'^(\d+[A-Z]*\s+|[A-Z]+\s+|\w+\s+\d+—)', current_line):
            # This is the start of an entry
            full_entry = current_line
            
            # Look ahead to see if the next line continues this entry
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                
                # If next line is empty, we're done with this entry
                if not next_line:
                    break
                    
                # If next line starts with a number/letter, it's a new entry
                if re.match(r'^(\d+[A-Z]*\s+|[A-Z]+\s+|\w+\s+\d+—)', next_line):
                    break
                    
                # If next line contains dots and ends with a number, it's the continuation with page number
                if re.search(r'\.+\s*\d+\s*$', next_line):
                    # Remove the dots and add the continuation
                    continuation = re.sub(r'\.+', '', next_line).strip()
                    full_entry += ' ' + continuation
                    j += 1
                    break
                    
                # Otherwise, it's a continuation line without dots
                full_entry += ' ' + next_line
                j += 1
            
            # Clean up the full entry - remove excessive dots
            full_entry = re.sub(r'\.{2,}', ' ', full_entry)  # Replace 2+ dots with space
            full_entry = re.sub(r'\s+', ' ', full_entry)      # Replace multiple spaces with single space
            full_entry = full_entry.strip()
            
            fixed_lines.append(full_entry)
            i = j
            
        else:
            # This might be a continuation line or header, add as is for now
            fixed_lines.append(current_line)
            i += 1
    
    return '\n'.join(fixed_lines)

def clean_extracted_text(text):
    """
    Cleans the extracted PDF text by removing header and footer content.
    
    :param text: Raw text extracted from PDF page
    :return: Cleaned text with only the essential content
    """
    # Find the start marker - content after "Compilation date: 21/02/2025"
    start_pattern = r"Compilation date: 21/02/2025"
    start_match = re.search(start_pattern, text)
    
    if start_match:
        # Get text after the compilation date
        text = text[start_match.end():]
    
    # Find and remove the end marker - "Authorised Version..." and everything after
    end_pattern = r"Authorised Version C2025C00194 registered 12/03/2025"
    end_match = re.search(end_pattern, text)
    
    if end_match:
        # Get text before the authorised version line
        text = text[:end_match.start()]
    
    # Clean up extra whitespace and asterisks
    text = re.sub(r'\*+', '', text)  # Remove asterisks
    text = re.sub(r'\n\s*\n', '\n', text)  # Remove multiple newlines
    text = text.strip()  # Remove leading/trailing whitespace
    
    # Fix broken lines and remove dot leaders
    text = fix_broken_lines(text)
    
    return text

def extract_and_clean_pdf_page(page_number, pdf_path='Migration Act 1958 – Volume 1.pdf'):
    """
    Extracts and cleans the text from the specified page number of the given PDF file.
    
    :param page_number: 1-based page number to extract
    :param pdf_path: Path to the PDF file
    :return: Cleaned text content
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        if page_number <= len(reader.pages):
            page = reader.pages[page_number - 1]
            raw_text = page.extract_text()
            cleaned_text = clean_extracted_text(raw_text)
            return cleaned_text
        else:
            print(f"PDF only has {len(reader.pages)} pages.")
            return None

# Example usage:
if __name__ == "__main__":
    for i in range(START_INDEX_PAGES, END_INDEX_PAGES + 1):
        print("=" * 120)
        print(f"PAGE {i} - CLEANED CONTENT:")
        print("=" * 120)
        cleaned_content = extract_and_clean_pdf_page(i)
        if cleaned_content:
            print(cleaned_content)
        print("=" * 120)
        print()