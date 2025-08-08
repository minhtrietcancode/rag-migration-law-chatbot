import re

def more_clean(txt_file_path):
    """
    Open the file, find the first occurrence of
    "Compilation No. 164 Compilation date: 21/02/2025",
    remove everything before and including it, then overwrite.
    """
    marker = "Compilation No. 164 Compilation date: 21/02/2025"

    # 1) Read full content
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 2) Locate the marker
    idx = text.find(marker)
    if idx == -1:
        # marker not found: leave file as-is (or you could clear it)
        return

    # 3) Compute the slice just after the marker
    start = idx + len(marker)

    # 4) Drop any leading whitespace/newlines after the slice
    remainder = text[start:].lstrip()

    # 5) Overwrite the file with the remainder
    with open(txt_file_path, 'w', encoding='utf-8') as f:
        f.write(remainder)

START = 1
END = 311

for i in range(START, END + 1):
    file_path = f"Migration Act Content Pages Txt Format/volume 2/page_{i}.txt"
    print("Cleaning page ", i)
    more_clean(file_path)