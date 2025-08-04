import json
from collections import OrderedDict

def move_cleaned_name_below_name(node):
    if isinstance(node, dict):
        new_node = OrderedDict()
        for key, value in node.items():
            new_node[key] = value
            if key == "name" and "cleaned_name" in node:
                new_node["cleaned_name"] = node["cleaned_name"]
        # Remove duplicate "cleaned_name" if it was already present
        if "cleaned_name" in new_node and list(new_node.keys()).count("cleaned_name") > 1:
            keys = list(new_node.keys())
            first = keys.index("cleaned_name")
            last = len(keys) - 1 - keys[::-1].index("cleaned_name")
            if first != last:
                del new_node[keys[last]]
        # Recursively process children
        for k, v in new_node.items():
            new_node[k] = move_cleaned_name_below_name(v)
        return new_node
    elif isinstance(node, list):
        return [move_cleaned_name_below_name(item) for item in node]
    else:
        return node

def reorder_metadata(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    new_data = move_cleaned_name_below_name(data)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

# Call the function with 2 json files
reorder_metadata("json_tree_index/volume_1_tree.json")
reorder_metadata("json_tree_index/volume_2_tree.json")