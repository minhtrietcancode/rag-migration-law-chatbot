import json
import re

def add_cleaned_names_to_tree(json_file_path: str):
    """
    Add 'cleaned_name' field to all nodes in the JSON tree file
    Removes page numbers from the end of names for all levels except root
    """
    # Read the existing JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        tree_data = json.load(f)
    
    def add_cleaned_name(node):
        """Recursively add cleaned_name to each node"""
        original_name = node.get('name', '')
        
        if node.get('type') == 'root':
            # For root node "Contents", cleaned_name is same as name
            cleaned_name = original_name
        else:
            # For all other levels (part, division, subdivision, section)
            # Remove page number from the end (last number after space)
            cleaned_name = re.sub(r'\s+\d+$', '', original_name).strip()
        
        # Add cleaned_name field
        node['cleaned_name'] = cleaned_name
        
        # Process children recursively
        for child in node.get('children', []):
            add_cleaned_name(child)
    
    # Process the entire tree
    add_cleaned_name(tree_data)
    
    # Save back to the same file
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(tree_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Added cleaned_name fields to {json_file_path}")

# Example usage:
if __name__ == "__main__":
    # Update both volume JSON files
    volume_1_json = 'json_tree_index/volume_1_tree.json'
    volume_2_json = 'json_tree_index/volume_2_tree.json'
    
    add_cleaned_names_to_tree(volume_1_json)
    add_cleaned_names_to_tree(volume_2_json)
    
    print("🎯 All JSON files updated with cleaned_name fields!")