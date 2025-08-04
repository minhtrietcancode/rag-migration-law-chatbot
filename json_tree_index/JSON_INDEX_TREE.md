# JSON Index Tree Structure for Migration Act 1958

This document describes the structure of the `merged_tree.json` file, which represents a hierarchical (tree-like) index of the Migration Act 1958 of Australia. The tree organizes the Act's contents by Volumes, Parts, Divisions, and Sections, capturing the logical and legal structure of the document.

## Top-Level Structure
- **Root Node**: The root node represents the entire contents and has the following properties:
  - `name`: Always "All contents"
  - `cleaned_name`: Cleaned version of the name
  - `type`: Always "merged root"
  - `children`: Array of volume nodes (e.g., Volume 1, Volume 2)

## Volume Nodes
- Each volume node represents a volume of the Act:
  - `name`: E.g., "Contents - Volume 1"
  - `cleaned_name`: Cleaned version of the name
  - `type`: Always "root"
  - `volume`: Volume number (1 or 2)
  - `children`: Array of part nodes

## Part Nodes
- Each part node represents a major part of the Act:
  - `name`: E.g., "Part 1—Preliminary 1"
  - `cleaned_name`: Cleaned version of the name
  - `type`: Always "part"
  - `children`: Array of division or section nodes


## Division Nodes
- Some parts are further divided into divisions:
  - `name`: E.g., "Division 1—Immigration status 60"
  - `cleaned_name`: Cleaned version of the name
  - `type`: Always "division"
  - `children`: Array of subdivision nodes or section nodes (or sometimes empty objects if section details are omitted)

## Subdivision Nodes
- Some divisions are further divided into subdivisions:
  - `name`: E.g., "Subdivision A—General provisions"
  - `cleaned_name`: Cleaned version of the name
  - `type`: Always "subdivision"
  - `children`: Array of section nodes (or sometimes empty objects if section details are omitted)

## Section Nodes
- The leaves of the tree are section nodes, representing individual sections of the Act:
  - `name`: E.g., "1 Short title 1"
  - `cleaned_name`: Cleaned version of the name
  - `type`: Always "section"
  - `start_page`: (optional) Start page number in the volume
  - `end_page`: (optional) End page number in the volume
  - `section_code`: Section identifier (e.g., "1", "5AA", "486A")

## Example Hierarchy
```
All contents (merged root)
├── Contents - Volume 1 (root)
│   ├── Part 1—Preliminary (part)
│   │   ├── 1 Short title (section)
│   │   ├── 2 Commencement (section)
│   │   └── ...
│   └── Part 2—Arrival, presence and departure of persons (part)
│       ├── Division 1—Immigration status (division)
│       │   ├── Section 13
│       │   └── ...
│       ├── Division 2—Power to obtain information... (division)
│       │   ├── Subdivision A—General provisions (subdivision)
│       │   │   ├── Section 18
│       │   │   └── ...
│       │   └── ...
│       └── ...
├── Contents - Volume 2 (root)
│   ├── Part 2—Arrival, presence and departure of persons (part)
│   │   ├── Division 14—Recovery of costs... (division)
│   │   │   ├── Section 262
│   │   │   └── ...
│   │   └── ...
│   └── ...
```

## Notes
- The tree is designed to allow traversal from the root down to individual sections, preserving the legal structure of the Act.
- The `cleaned_name` field is a normalized version of the `name` for easier processing.
- Page numbers (`start_page`, `end_page`) are included where available for reference.

---
This structure enables programmatic navigation, search, and referencing of the Migration Act 1958's contents for applications such as legal research, chatbots, or document analysis.