import json
import re
from typing import Dict, List, Any

def parse_migration_act_contents(file_path: str) -> Dict[str, Any]:
    """
    Parse the Migration Act contents into a hierarchical tree structure
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
        subdivision_match = re.match(r'^(Subdivision\s+[A-Z]+[A-Z]*—.+)$', line)
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
            header_section = {
                "name": header_match.group(1),
                "type": "section"
            }
            
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
    
    return tree

# Calling the function with 2 volume index .txt files
file_path_volume_1 = 'extracted_index_pages/Volume 1/completed_volume_1_indexes.txt'
tree_structure_volume_1 = parse_migration_act_contents(file_path_volume_1)

file_path_volume_2 = 'extracted_index_pages/Volume 2/completed_volume_2_indexes.txt'
tree_structure_volume_2 = parse_migration_act_contents(file_path_volume_2)


# Save to JSON file
output_file_volume_1 = 'json_tree_index/volume_1_tree.json'
with open(output_file_volume_1, 'w', encoding='utf-8') as f:
    json.dump(tree_structure_volume_1, f, indent=2, ensure_ascii=False)

output_file_volume_2 = 'json_tree_index/volume_2_tree.json'
with open(output_file_volume_2, 'w', encoding='utf-8') as f:
    json.dump(tree_structure_volume_2, f, indent=2, ensure_ascii=False)