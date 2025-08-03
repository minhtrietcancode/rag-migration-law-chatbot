import PyPDF2
import re
import contextlib

# start and end pages of volume 1
START_INDEX_PAGES_VOLUME_1 = 3
END_INDEX_PAGES_VOLUME_1 = 25

# start and end pages of volume 2
START_INDEX_PAGES_VOLUME_2 = 3
END_INDEX_PAGES_VOLUME_2 = 18

def fix_subdivision_splits(text):
    """
    Fixes subdivision entries that got concatenated with previous lines.
    Only splits when Subdivision is NOT at the start of a line.
    """
    # Updated pattern to match any characters/numbers in the code
    # and handle both em dash (—) and regular hyphen (-)
    subdivision_pattern = r'(\S+.*?)(Subdivision\s+[A-Za-z0-9]+[—-])'
    return re.sub(subdivision_pattern, r'\1\n\2', text)

def fix_division_splits(text):
    """
    Fixes division entries that got concatenated with previous lines.
    Only splits when Division is NOT at the start of a line.
    """
    # Updated pattern to match any characters/numbers in the code
    # and handle both em dash (—) and regular hyphen (-)
    division_pattern = r'(\S+.*?)(Division\s+[A-Za-z0-9]+[—-])'
    return re.sub(division_pattern, r'\1\n\2', text)

def fix_all_splits(text):
    """
    Applies division and subdivision fixes repeatedly until no more changes.
    """
    max_iterations = 5
    for _ in range(max_iterations):
        prior = text
        text = fix_division_splits(text)
        text = fix_subdivision_splits(text)
        if text == prior:
            break
    return text

def fix_broken_lines(text):
    """
    Fixes broken lines in the table of contents and removes dot leaders.
    """
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        curr = lines[i].strip()
        if not curr:
            i += 1
            continue

        # If it's a TOC entry, stitch following lines
        if re.match(r'^(\d+[A-Z]*\s+|Part\s+\d+|Division\s+\d+|Subdivision\s+[A-Z]+)', curr):
            full = curr
            j = i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if not nxt or re.match(r'^(\d+[A-Z]*\s+|Part\s+\d+|Division\s+\d+|Subdivision\s+[A-Z]+)', nxt):
                    break
                full += ' ' + nxt
                j += 1
                if re.search(r'\d+\s*$', nxt):
                    break

            # cleanup
            full = re.sub(r'\.{2,}', ' ', full)
            full = re.sub(r'\s+', ' ', full).strip()
            result.append(full)
            i = j
        else:
            result.append(curr)
            i += 1

    return '\n'.join(result)

def clean_extracted_text(text):
    """
    Cleans the extracted PDF text by removing header/footer and fixing formatting.
    """
    # strip header
    header_pat = r"Compilation date: 21/02/2025"
    m = re.search(header_pat, text)
    if m:
        text = text[m.end():]

    # strip footer
    footer_pat = r"Authorised Version C2025C00194 registered 12/03/2025"
    m = re.search(footer_pat, text)
    if m:
        text = text[:m.start()]

    # basic cleanup
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'\n\s*\n', '\n', text).strip()

    # fix splits & broken lines
    text = fix_all_splits(text)
    text = fix_broken_lines(text)
    return text

def extract_and_clean_pdf_page(page_number, pdf_path):
    """
    Extracts and cleans text from a specific PDF page.
    """
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        total = len(reader.pages)
        if page_number > total:
            print(f"PDF only has {total} pages.")
            return None

        raw = reader.pages[page_number - 1].extract_text()
        return clean_extracted_text(raw)

def extract_pdf_indexes(pdf_path, output_txt_path, start_page, end_page):
    """
    Extracts indexes from PDF pages and writes to output file.
    
    Args:
        pdf_path (str): Path to the input PDF file
        output_txt_path (str): Path to the output text file
        start_page (int): Starting page number for extraction
        end_page (int): Ending page number for extraction
    """
    with open(output_txt_path, 'w', encoding='utf-8') as logfile, \
         contextlib.redirect_stdout(logfile):

        for i in range(start_page, end_page + 1):
            print("=" * 120)
            print(f"PAGE {i} - CLEANED CONTENT:")
            print("=" * 120)

            content = extract_and_clean_pdf_page(i, pdf_path)
            if content:
                print(content)

            print("=" * 120)
            print()

if __name__ == "__main__":
    # Process Volume 1
    # extract_pdf_indexes('Migration Act 1958 – Volume 1.pdf', 
    #                    'extracted_index_pages/Volume 1/volume_1_indexes.txt',
    #                    START_INDEX_PAGES_VOLUME_1, 
    #                    END_INDEX_PAGES_VOLUME_1)
    
    # Process Volume 2
    extract_pdf_indexes('Migration Act 1958 – Volume 2.pdf', 
                       'extracted_index_pages/Volume 2/volume_2_indexes.txt',
                       START_INDEX_PAGES_VOLUME_2, 
                       END_INDEX_PAGES_VOLUME_2)