
import json
import os

def merge_tree_json(volume1_path, volume2_path, output_path):
    """
    Merge two tree-like JSON files into a new tree with a root 'All contents'.
    The children of the new root will be the roots of the two input trees.
    """
    with open(volume1_path, 'r', encoding='utf-8') as f1:
        tree1 = json.load(f1)
    with open(volume2_path, 'r', encoding='utf-8') as f2:
        tree2 = json.load(f2)

    merged_tree = {
        "name": "All contents",
        "cleaned_name": "All contents",
        "type": "merged root",
        "children": [tree1, tree2]
    }

    with open(output_path, 'w', encoding='utf-8') as fout:
        json.dump(merged_tree, fout, ensure_ascii=False, indent=2)

# Example usage:
merge_tree_json(
    'json_tree_index/volume_1_tree.json',
    'json_tree_index/volume_2_tree.json',
    'json_tree_index/merged_tree.json'
)
