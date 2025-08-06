import json

sections = []

with open("json_search_tree/all_vol_section_hashmap.json", "r", encoding="utf-8") as f:
    hashmap = json.load(f)

    vol1 = hashmap["volume 1"]
    vol1_sections = list(vol1.keys())

    vol2 = hashmap["volume 2"]
    vol2_sections = list(vol2.keys())

    for sec in vol1_sections: 
        sections.append(sec)

    for section in vol2_sections:
        sections.append(section)

print(len(sections) == len(set(sections)))


