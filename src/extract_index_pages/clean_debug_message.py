import re
import os

def clean_pdf_text(file_path):
    """
    Clean debug lines from extracted PDF text file and save to a new file.
    
    Args:
        file_path (str): Relative path to the .txt file to be cleaned
    
    Returns:
        str: Path to the newly created cleaned file
    """
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split content into lines for processing
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip the exact debug patterns from your example
            debug_lines = "=" * 120
            if line.strip() == debug_lines or \
               line.strip().startswith('PAGE') and 'CLEANED CONTENT:' in line or \
                line == "":
                continue
            
            # Add non-debug lines to cleaned content
            cleaned_lines.append(line)
        
        # Join the cleaned lines back together
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Remove excessive empty lines (more than 2 consecutive empty lines)
        cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
        
        # Generate the new filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1]
        
        new_filename = f"completed_{name_without_ext}{extension}"
        new_file_path = os.path.join(directory, new_filename)
        
        # Write the cleaned content to the new file
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content.strip())
        
        print(f"✅ Successfully cleaned file: {file_path}")
        print(f"📄 Saved cleaned content to: {new_file_path}")
        
        return new_file_path
        
    except FileNotFoundError:
        print(f"❌ Error: File not found - {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error processing file {file_path}: {str(e)}")
        return None

# Batch processing function (bonus)
def clean_multiple_files(file_paths):
    """
    Clean multiple PDF text files at once.
    
    Args:
        file_paths (list): List of file paths to clean
    
    Returns:
        list: List of paths to the newly created cleaned files
    """
    cleaned_files = []
    
    for file_path in file_paths:
        cleaned_file = clean_pdf_text(file_path)
        if cleaned_file:
            cleaned_files.append(cleaned_file)
    
    return cleaned_files

# Call the function 
files_to_clean = ["extracted_index_pages/Volume 1/volume_1_indexes.txt", "extracted_index_pages/Volume 2/volume_2_indexes.txt"]
cleaned_files = clean_multiple_files(files_to_clean)