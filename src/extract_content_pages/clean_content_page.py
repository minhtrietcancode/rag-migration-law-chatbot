
def clean_extracted_text(extracted_text):
    """
    Cleans the extracted text by:
    1. Removing the first, second, and third non-empty lines
    2. In the fourth non-empty line, remove everything up to and including '21/02/2025'
    3. Removing the last non-empty line
    4. Preserving empty lines between content
    Args:
        extracted_text (str): The raw extracted text from the PDF page
    Returns:
        str: The cleaned text
    """
    # Split into lines and filter out empty lines for processing
    lines = extracted_text.splitlines()
    non_empty_lines = [line for line in lines if line.strip() != '']
    if len(non_empty_lines) < 5:
        # Not enough lines to process as expected, return empty or original
        return ''

    # Remove first 3 non-empty lines
    cleaned_lines = non_empty_lines[3:]

    # Clean the 4th non-empty line (now at index 0)
    target = '21/02/2025'
    if target in cleaned_lines[0]:
        idx = cleaned_lines[0].find(target)
        cleaned_lines[0] = cleaned_lines[0][idx + len(target):].lstrip()

    # Remove the last non-empty line
    cleaned_lines = cleaned_lines[:-1]

    # Reconstruct the cleaned text, preserving original empty lines between content
    # We'll use the original lines, but only keep those that match the cleaned non-empty lines, in order
    result = []
    cleaned_iter = iter(cleaned_lines)
    for line in lines:
        if line.strip() == '':
            result.append(line)
        else:
            try:
                next_clean = next(cleaned_iter)
                result.append(next_clean)
            except StopIteration:
                break
    return '\n'.join(result)
