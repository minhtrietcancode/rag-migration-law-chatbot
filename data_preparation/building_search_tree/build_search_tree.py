MERGED_TREE_INDEX_ALL_VOL_PATH = "json_tree_index/merged_tree.json"
ALL_VOL_SEARCH_TREE_PATH = "json_search_tree/all_vol_search_tree.json"

import json

def build_cleaned_tree(node):
    node_type = node.get("type")
    cleaned_name = node.get("cleaned_name")
    children = node.get("children", [])

    # If this is a list of sections, return the special list format
    if children and all(child.get("type") == "section" for child in children if isinstance(child, dict)):
        # Only keep [cleaned_name, section_code] for each section
        return [
            [child["cleaned_name"], child["section_code"]]
            for child in children if child.get("type") == "section"
        ]

    # Otherwise, build a dict of cleaned_name: subtree
    result = {}
    for child in children:
        if not isinstance(child, dict):
            continue
        key = child.get("cleaned_name")
        if not key:
            continue
        subtree = build_cleaned_tree(child)
        result[key] = subtree
    return result

def main():
    with open(MERGED_TREE_INDEX_ALL_VOL_PATH, "r", encoding="utf-8") as f:
        merged_tree = json.load(f)

    # Find the two volumes
    volumes = [child for child in merged_tree["children"] if child.get("type") == "root"]
    tree = {}
    for vol in volumes:
        vol_num = vol.get("volume")
        vol_key = f"Volume {vol_num}"
        tree[vol_key] = build_cleaned_tree(vol)

    final_tree = {"Migration Act 1958": tree}

    # Save to a new file
    output_path = ALL_VOL_SEARCH_TREE_PATH
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_tree, f, ensure_ascii=False, indent=2)
    print(f"Cleaned tree saved to {output_path}")

if __name__ == "__main__":
    main()

