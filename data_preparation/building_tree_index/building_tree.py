import json
import re
from typing import Dict, List, Any
import os

def parse_migration_act_contents(file_path: str) -> Dict[str, Any]:
    """
    Parse the Migration Act contents into a hierarchical tree structure
    Also extracts start and end page numbers for each section
    """
    # Read the content from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    lines = content.strip().split('\n')
    
    # Initialize the root
    tree = {
        "name": "Contents",
        "type": "root",
        "children": []
    }
    
    current_part = None
    current_division = None
    current_subdivision = None
    
    # Store all sections to calculate end pages later
    all_sections = []
    
    for line in lines:
        line = line.strip()
        if not line or line == "Contents":
            continue
            
        # Check for Part pattern: "Part X—description"
        part_match = re.match(r'^(Part\s+\d+[A-Z]*—.+)$', line)
        if part_match:
            current_part = {
                "name": part_match.group(1),
                "type": "part",
                "children": []
            }
            tree["children"].append(current_part)
            current_division = None
            current_subdivision = None
            continue
            
        # Check for Division pattern: "Division X—description"
        division_match = re.match(r'^(Division\s+\d+[A-Z]*—.+)$', line)
        if division_match:
            current_division = {
                "name": division_match.group(1),
                "type": "division", 
                "children": []
            }
            if current_part:
                current_part["children"].append(current_division)
            current_subdivision = None
            continue
            
        # Check for Subdivision pattern: "Subdivision X—description"
        subdivision_match = re.match(r'^(Subdivision\s+[A-Z]+—.+)$', line)
        if subdivision_match:
            current_subdivision = {
                "name": subdivision_match.group(1),
                "type": "subdivision",
                "children": []
            }
            if current_division:
                current_division["children"].append(current_subdivision)
            elif current_part:
                current_part["children"].append(current_subdivision)
            continue
            
        # Everything else should be header sections (numbered items)
        # Pattern: number/code followed by description and page number
        header_match = re.match(r'^(\d+[A-Z]*\s+.+)$', line)
        if header_match:
            # Extract page number from the end of the line
            page_match = re.search(r'\s(\d+)$', line)
            start_page = int(page_match.group(1)) if page_match else None
            
            header_section = {
                "name": header_match.group(1),
                "type": "section",
                "start_page": start_page,
                "end_page": None  # Will be calculated later
            }
            
            # Store reference for end page calculation
            all_sections.append(header_section)
            
            # Add to the most specific current container
            if current_subdivision:
                current_subdivision["children"].append(header_section)
            elif current_division:
                current_division["children"].append(header_section)
            elif current_part:
                current_part["children"].append(header_section)
            else:
                # Fallback to root if no part is active
                tree["children"].append(header_section)
    
    # Calculate end pages for all sections
    for i, section in enumerate(all_sections):
        if i < len(all_sections) - 1:
            # End page is one less than the next section's start page
            next_start = all_sections[i + 1]["start_page"]
            if next_start is not None and section["start_page"] is not None:
                section["end_page"] = next_start
        # Last section doesn't have an end page calculated
    
    return tree

def create_directories_if_not_exist(file_path: str):
    """Create directories if they don't exist"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

# Main execution
if __name__ == "__main__":
    # File paths for the two volumes
    file_path_volume_1 = 'extracted_index_pages/Volume 1/completed_volume_1_indexes.txt'
    file_path_volume_2 = 'extracted_index_pages/Volume 2/completed_volume_2_indexes.txt'
    
    # Output file paths
    output_file_volume_1 = 'json_tree_index/volume_1_tree.json'
    output_file_volume_2 = 'json_tree_index/volume_2_tree.json'
    
    # Create output directories if they don't exist
    create_directories_if_not_exist(output_file_volume_1)
    create_directories_if_not_exist(output_file_volume_2)
    
    # Process Volume 1
    if os.path.exists(file_path_volume_1):
        print("Processing Volume 1...")
        tree_structure_volume_1 = parse_migration_act_contents(file_path_volume_1)
        
        # Save to JSON file
        with open(output_file_volume_1, 'w', encoding='utf-8') as f:
            json.dump(tree_structure_volume_1, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Volume 1 tree structure saved to {output_file_volume_1}")
    else:
        print(f"❌ Volume 1 file not found: {file_path_volume_1}")
    
    # Process Volume 2
    if os.path.exists(file_path_volume_2):
        print("Processing Volume 2...")
        tree_structure_volume_2 = parse_migration_act_contents(file_path_volume_2)
        
        # Save to JSON file
        with open(output_file_volume_2, 'w', encoding='utf-8') as f:
            json.dump(tree_structure_volume_2, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Volume 2 tree structure saved to {output_file_volume_2}")
    else:
        print(f"❌ Volume 2 file not found: {file_path_volume_2}")