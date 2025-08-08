import json

CURRENT_SEARCH_TREE_PATH = "json_search_tree/all_vol_search_tree.json"
FINAL_SEARCH_TREE_PATH = "json_search_tree/final_search_tree.json"

def process_node(node, volume):
    if isinstance(node, list):
        # Check if this is a leaf node: [name, code]
        if len(node) == 2 and all(isinstance(x, str) for x in node):
            return f"{node[0]}_{node[1]}_{volume}"
        # Otherwise, process each element
        return [process_node(child, volume) for child in node]
    elif isinstance(node, dict):
        return {k: process_node(v, volume) for k, v in node.items()}
    else:
        return node

def build_final_search_tree():
    with open(CURRENT_SEARCH_TREE_PATH, "r", encoding="utf-8") as f:
        tree = json.load(f)

    result = {}
    for act, volumes in tree.items():
        result[act] = {}
        for vol in volumes:
            result[act][vol] = process_node(volumes[vol], vol)

    with open(FINAL_SEARCH_TREE_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_final_search_tree()