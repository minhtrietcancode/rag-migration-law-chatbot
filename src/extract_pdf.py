import PyPDF2
import re

START_INDEX_PAGES = 3
END_INDEX_PAGES = 25
PDF_PATH = 'Migration Act 1958 – Volume 1.pdf'
OUTPUT_PATH = 'indexes.txt'

def fix_subdivision_splits(text):
    """
    Fixes subdivision entries that got concatenated with previous lines.
    """
    subdivision_pattern = r'(\s+)(Subdivision\s+[A-Z]+—)'
    return re.sub(subdivision_pattern, r'\n\2', text)

def fix_division_splits(text):
    """
    Fixes division entries that got concatenated with previous lines.
    """
    division_pattern = r'(\s+)(Division\s+[0-9A-Z]+—)'
    return re.sub(division_pattern, r'\n\2', text)

def fix_broken_lines(text):
    """
    Fixes broken lines in the table of contents and removes dot leaders.
    """
    lines = text.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        current_line = lines[i].strip()
        if not current_line:
            i += 1
            continue

        if re.match(r'^(\d+[A-Z]*\s+|[A-Z]+\s+|\w+\s+\d+—)', current_line):
            full_entry = current_line
            j = i + 1

            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line:
                    break
                if re.match(r'^(\d+[A-Z]*\s+|[A-Z]+\s+|\w+\s+\d+—)', next_line):
                    break
                if re.search(r'\.+\s*\d+\s*$', next_line):
                    continuation = re.sub(r'\.+', '', next_line).strip()
                    full_entry += ' ' + continuation
                    j += 1
                    break
                full_entry += ' ' + next_line
                j += 1

            full_entry = re.sub(r'\.{2,}', ' ', full_entry)
            full_entry = re.sub(r'\s+', ' ', full_entry).strip()
            fixed_lines.append(full_entry)
            i = j
        else:
            fixed_lines.append(current_line)
            i += 1

    return '\n'.join(fixed_lines)

def clean_extracted_text(text):
    """
    Cleans the extracted PDF text by removing header/footer content,
    fixing subdivision & division splits, and broken lines.
    """
    # strip everything before compilation date
    start_match = re.search(r"Compilation date: 21/02/2025", text)
    if start_match:
        text = text[start_match.end():]

    # strip everything after authorised version
    end_match = re.search(r"Authorised Version C2025C00194 registered 12/03/2025", text)
    if end_match:
        text = text[:end_match.start()]

    text = re.sub(r'\*+', '', text)
    text = re.sub(r'\n\s*\n', '\n', text).strip()
    text = fix_subdivision_splits(text)
    text = fix_division_splits(text)
    text = fix_broken_lines(text)
    return text

def extract_and_clean_pdf_page(page_number, pdf_path=PDF_PATH):
    """
    Extracts and cleans the text from a specified PDF page.
    Returns cleaned text, or a debug message if the page is out of range.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total = len(reader.pages)

        if page_number <= total:
            raw = reader.pages[page_number - 1].extract_text() or ''
            return clean_extracted_text(raw)
        else:
            return f"DEBUG: PDF only has {total} pages, asked for page {page_number}."

if __name__ == "__main__":
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out_f:
        for i in range(START_INDEX_PAGES, END_INDEX_PAGES + 1):
            sep = "=" * 120
            out_f.write(sep + "\n")
            out_f.write(f"PAGE {i} - CLEANED CONTENT:\n")
            out_f.write(sep + "\n")

            result = extract_and_clean_pdf_page(i)
            out_f.write(result + "\n")

            out_f.write(sep + "\n\n")

    print(f"All pages processed. Results written to {OUTPUT_PATH}")