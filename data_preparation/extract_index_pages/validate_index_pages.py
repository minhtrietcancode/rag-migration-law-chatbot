import re

def validate_cleaned_text(file_path):
    """
    Validate if the cleaned text follows the correct patterns.
    
    Args:
        file_path (str): Path to the cleaned text file
    
    Returns:
        dict: Validation results with details
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        valid_lines = []
        invalid_lines = []
        
        for i, line in enumerate(lines, 1):
            if is_valid_line(line):
                valid_lines.append((i, line))
            else:
                invalid_lines.append((i, line))
        
        # Prepare results
        total_lines = len(lines)
        valid_count = len(valid_lines)
        invalid_count = len(invalid_lines)
        
        results = {
            'file_path': file_path,
            'total_lines': total_lines,
            'valid_lines': valid_count,
            'invalid_lines': invalid_count,
            'is_valid': invalid_count == 0,
            'success_rate': (valid_count / total_lines * 100) if total_lines > 0 else 0,
            'invalid_details': invalid_lines
        }
        
        # Print results
        print(f"📄 Validating file: {file_path}")
        print(f"📊 Total lines: {total_lines}")
        print(f"✅ Valid lines: {valid_count}")
        print(f"❌ Invalid lines: {invalid_count}")
        print(f"📈 Success rate: {results['success_rate']:.1f}%")
        
        if invalid_lines:
            print(f"\n🚨 Invalid lines found:")
            for line_num, line_content in invalid_lines:
                print(f"  Line {line_num}: {line_content}")
        else:
            print(f"\n🎉 All lines are valid!")
        
        return results
        
    except FileNotFoundError:
        print(f"❌ Error: File not found - {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error validating file {file_path}: {str(e)}")
        return None

def is_valid_line(line):
    """
    Check if a single line follows the valid patterns.
    
    Args:
        line (str): Line to validate
    
    Returns:
        bool: True if line is valid, False otherwise
    """
    line = line.strip()
    
    # Pattern 1: Just "Contents"
    if line == "Contents":
        return True
    
    # Pattern 2: "Part " followed by content, "—", more content, ending with number
    if line.startswith("Part "):
        return re.match(r'^Part .+—.+ \d+$', line) is not None
    
    # Pattern 3: "Division " with same rule as Part
    if line.startswith("Division "):
        return re.match(r'^Division .+—.+ \d+$', line) is not None
    
    # Pattern 4: "Subdivision " with same rule as Part
    if line.startswith("Subdivision "):
        return re.match(r'^Subdivision .+—.+ \d+$', line) is not None
    
    # Pattern 5: Section codes (numbers or numbers+letters) followed by content and ending number
    # Examples: "1 Short title 1", "4AA Detention of minors a last resort 4", "13 Lawful non-citizens 60"
    section_pattern = r'^(\d+[A-Z]*) .+ \d+$'
    if re.match(section_pattern, line):
        return True
    
    return False

# Example usage and testing
if __name__ == "__main__":    
    # Validate a file (replace with your actual file path)
    validate_cleaned_text("extracted_index_pages/Volume 1/completed_volume_1_indexes.txt")
    validate_cleaned_text("extracted_index_pages/Volume 2/completed_volume_2_indexes.txt")