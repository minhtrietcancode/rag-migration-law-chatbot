import json
import os

def extract_section_first_terms(json_file_path):
    """
    Given a relative path to a JSON file, load the file and recursively extract the first term of the 'name' field from every node of type 'section'.
    Args:
        json_file_path (str): Relative path to the JSON file.
    Returns:
        List[str]: List of first terms from 'section' nodes.
    """
    # Resolve to absolute path if needed
    abs_path = os.path.abspath(json_file_path)
    with open(abs_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    def recurse(node):
        if isinstance(node, dict):
            if node.get('type') == 'section' and 'name' in node:
                first_term = node['name'].split()[0]
                node['section_code'] = first_term
            if 'children' in node and isinstance(node['children'], list):
                for child in node['children']:
                    recurse(child)
        elif isinstance(node, list):
            for item in node:
                recurse(item)

    recurse(json_data)

    # Write the modified JSON back to the file (in-place update)
    with open(abs_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

# Call the function with the 2 json files 
extract_section_first_terms("json_tree_index/volume_1_tree.json")
extract_section_first_terms("json_tree_index/volume_2_tree.json")