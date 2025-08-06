# JSON Search Tree Directory

This directory contains **optimized, short-form JSON files** derived from the full metadata tree in `json_tree_index/merged_tree.json`. These files are specifically designed to support efficient search, retrieval, and programmatic navigation of the Migration Act 1958 for downstream applications such as chatbots, legal research tools, or document viewers.

**Purpose of these files:**
- They are _optimized versions_ of the much larger and more detailed `merged_tree.json`.
- The search tree file keeps only the names and hierarchy, making it ideal for embedding and fast traversal.
- The hashmap file enables O(1) lookup of section metadata, using the names obtained after tree search.

## Files

### 1. `all_vol_search_tree.json`
- **Purpose:**
  - Provides a **condensed, hierarchical tree** of the Migration Act 1958, including both Volume 1 and Volume 2.
  - Mirrors the logical structure of the Act: Act → Volume → Part → Division → Subdivision → Section, but omits extra metadata to keep the structure lightweight.
  - Each node contains only the names (for embedding and navigation), with lists of sections as `[section_title, section_code]` pairs or further nested dictionaries for deeper levels.
  - This file is a _short version_ of the tree in `json_tree_index/merged_tree.json`, optimized for fast traversal and embedding.
- **Usage:**
  - Enables traversal and exploration of the Act's structure in a way that matches the document's logical organization.
  - Useful for building navigation trees, generating tables of contents, or visualizing the Act's hierarchy.
  - Use this file to search for a section or node by name, then use the hashmap for fast metadata lookup.

### 2. `all_vol_section_hashmap.json`
- **Purpose:**
  - Provides a **flat, hash-mapped structure** for O(1) lookup of section metadata.
  - Maps unique section identifiers (e.g., `Short title_1`, `Commencement_2`) to their metadata, such as the starting and ending page number.
  - Organized by volume for clarity and separation.
  - This file is also a _short version_ derived from `merged_tree.json`, and is intended to be used after a name is found via the search tree.
- **Usage:**
  - Enables instant access to section metadata without traversing the full tree.
  - Ideal for quickly resolving section codes or titles to their page numbers or other attributes.
  - Supports fast search and retrieval in chatbot or search applications.
  - Use this file for O(1) lookup of section metadata after finding the section name via the search tree.

## Example Use Cases
- **Hierarchical Navigation:** Use `all_vol_search_tree.json` to build a navigation UI or to programmatically walk the Act's structure.
- **Direct Section Lookup:** Use `all_vol_section_hashmap.json` to instantly retrieve metadata (like page numbers) for a given section code or title.
- **Combined Usage:** Traverse the tree for context, then use the hashmap for fast metadata access.

## Why This Structure?
- The tree structure (`all_vol_search_tree.json`) is a **condensed, human-readable version** of the full tree, ideal for navigation, embedding, and fast searching by name.
- The hashmap structure (`all_vol_section_hashmap.json`) is **optimized for speed**, allowing O(1) access to section data, which is critical for search and retrieval tasks in large legal documents.
- Both are _shortened, purpose-built_ versions of `json_tree_index/merged_tree.json`.

---

**In summary:**
- Use the search tree for structure, navigation, and embedding.
- Use the hashmap for fast, direct lookups after searching by name.

These files together enable both intuitive exploration and high-performance search of the Migration Act 1958's contents, while keeping only the essential data needed for fast search and retrieval.
