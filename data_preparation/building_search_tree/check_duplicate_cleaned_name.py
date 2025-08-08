import json
from collections import defaultdict, Counter
import os

# Path to the merged tree JSON file
MERGED_TREE_PATH = os.path.join('json_tree_index', 'merged_tree.json')

def load_merged_tree(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def collect_nodes(tree, volume, type_filter):
    """
    Recursively collect nodes of a given type from the tree for a specific volume.
    """
    result = []
    def _collect(node):
        if node.get('volume') == volume and node.get('type') == type_filter:
            result.append(node)
        for child in node.get('children', []):
            _collect(child)
    _collect(tree)
    return result

def check_duplicates(nodes):
    cleaned_names = [n['cleaned_name'] for n in nodes if 'cleaned_name' in n]
    counter = Counter(cleaned_names)
    return {name: count for name, count in counter.items() if count > 1}

def main():
    tree = load_merged_tree(MERGED_TREE_PATH)
    # Find all volumes
    volumes = set()
    def find_volumes(node):
        if 'volume' in node:
            volumes.add(node['volume'])
        for child in node.get('children', []):
            find_volumes(child)
    find_volumes(tree)
    types = ['part', 'division', 'subdivision']
    for volume in sorted(volumes):
        print(f'Checking volume: {volume}')
        for t in types:
            nodes = collect_nodes(tree, volume, t)
            dups = check_duplicates(nodes)
            if dups:
                print(f'  Duplicate cleaned_name(s) for type "{t}" in volume "{volume}":')
                for name, count in dups.items():
                    print(f'    "{name}": {count} times')
            else:
                print(f'  No duplicates for type "{t}" in volume "{volume}".')

if __name__ == '__main__':
    main()

# OKAY ALL GOOD, NO DUPLICATED AT ALL, HERE IS THE RESULT WHEN RUNNING IN THE TERMINAL 
'''
Checking volume: 1
  No duplicates for type "part" in volume "1".
  No duplicates for type "division" in volume "1".
  No duplicates for type "subdivision" in volume "1".
Checking volume: 2
  No duplicates for type "part" in volume "2".
  No duplicates for type "division" in volume "2".
  No duplicates for type "subdivision" in volume "2".
'''