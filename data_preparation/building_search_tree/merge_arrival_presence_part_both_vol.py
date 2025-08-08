import json
import uuid

FINAL_SEARCH_TREE_PATH = "json_search_tree/final_search_tree.json"
OPTIMIZED_SEARCH_TREE_PATH = "json_search_tree/optimized_tree.json"

# remember that this one would be the value for the key "Arrival, presence and departure of persons"
merged_arrival = {}

# setup a dict to load the current final tree
tree = {}

with open(FINAL_SEARCH_TREE_PATH, "r", encoding="utf-8") as f:
    tree = json.load(f)

    # volume 1 arrival, presence .. part 
    vol_1_arrival = tree['Migration Act 1958']['Volume 1']['Arrival, presence and departure of persons']

    # volume 2 arrival, presence .. part 
    vol_2_arrival = tree['Migration Act 1958']['Volume 2']['Arrival, presence and departure of persons']

    # merge the things belong to same part but in different volumes
    merged_arrival.update(vol_1_arrival)
    merged_arrival.update(vol_2_arrival)


# This will be the new dict for searching, removing root and volume levels
new_dict = {}

# Get all part-level keys from both volumes
vol_1_parts = tree['Migration Act 1958']['Volume 1']
vol_2_parts = tree['Migration Act 1958']['Volume 2']


# Add parts from volume 1 in order
for part in vol_1_parts.keys():
    if part == 'Arrival, presence and departure of persons':
        new_dict[part] = merged_arrival
    else:
        new_dict[part] = vol_1_parts[part]

# Add parts from volume 2 that are not already in new_dict
for part in vol_2_parts.keys():
    if part not in new_dict:
        new_dict[part] = vol_2_parts[part]

# Write the new dict to a new JSON file
with open(OPTIMIZED_SEARCH_TREE_PATH, "w", encoding="utf-8") as f:
    json.dump(new_dict, f, ensure_ascii=False, indent=2)


