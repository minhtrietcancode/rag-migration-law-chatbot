import json
import os

ALL_VOL_SECTION_HASHMAP_PATH = "json_search_tree/all_vol_section_hashmap.json"
MERGED_TREE_INDEX_ALL_VOL_PATH = "json_tree_index/merged_tree.json"

def collect_sections(node, hashmap, volume):
    if isinstance(node, dict):
        # Only hash sections with start_page and end_page
        if (node.get("type") == "section" 
            and "cleaned_name" in node 
            and "start_page" in node 
            and "end_page" in node
            and "section_code" in node):
            name = node["cleaned_name"]
            section_code = str(node["section_code"])
            key = f"{name}_{section_code}"
            if key in hashmap[volume]:
                print(f"[DUPLICATE] {key} already exists in volume {volume}")
            hashmap[volume][key] = {
                "start_page": node["start_page"],
                "end_page": node["end_page"]
            }
        # Recurse into children if present
        if "children" in node and isinstance(node["children"], list):
            for child in node["children"]:
                collect_sections(child, hashmap, volume)

def build_section_hashmap():
    with open(MERGED_TREE_INDEX_ALL_VOL_PATH, "r", encoding="utf-8") as f:
        merged_tree = json.load(f)

    hashmap = {"volume 1": {}, "volume 2": {}}

    for child in merged_tree.get("children", []):
        if child.get("type") == "root" and "volume" in child:
            volume = f"volume {child['volume']}"
            collect_sections(child, hashmap, volume)

    # Save to JSON
    os.makedirs(os.path.dirname(ALL_VOL_SECTION_HASHMAP_PATH), exist_ok=True)
    with open(ALL_VOL_SECTION_HASHMAP_PATH, "w", encoding="utf-8") as f:
        json.dump(hashmap, f, indent=2, ensure_ascii=False)
    print(f"Hashmap saved to {ALL_VOL_SECTION_HASHMAP_PATH}")

if __name__ == "__main__":
    build_section_hashmap()

