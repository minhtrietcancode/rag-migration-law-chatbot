import json
import os

CURRENT_HASHMAP_PATH = "json_search_tree/all_vol_section_hashmap.json"
FINAL_HASHMAP_PATH = "json_search_tree/final_hashmap.json"

def build_flat_hashmap():
    with open(CURRENT_HASHMAP_PATH, "r", encoding="utf-8") as f:
        old_hashmap = json.load(f)

    new_hashmap = {}

    for vol_key in ["volume 1", "volume 2"]:
        if vol_key not in old_hashmap:
            continue
        for section, value in old_hashmap[vol_key].items():
            new_key = f"{section}_Volume 1" if vol_key == "volume 1" else f"{section}_Volume 2"
            # Copy the entire value dict as is
            new_hashmap[new_key] = value.copy()

    with open(FINAL_HASHMAP_PATH, "w", encoding="utf-8") as f:
        json.dump(new_hashmap, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    build_flat_hashmap()

