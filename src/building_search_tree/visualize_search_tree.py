import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from collections import defaultdict

class EnhancedTreeVisualizer:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.tree_data = None
        self.node_positions = {}
        self.fig = None
        self.ax = None
        
        # Enhanced spacing parameters
        self.node_width = 3.0
        self.node_height = 0.8
        self.min_horizontal_spacing = 4.0
        self.level_height = 2.0
        self.margin = 1.0
        
        # Node type colors - High contrast colors for better visibility
        self.colors = {
            'root': {'face': '#FF6B6B', 'edge': '#D63031', 'text': 'white'},      # Red
            'volume': {'face': '#4ECDC4', 'edge': '#00B894', 'text': 'black'},    # Teal
            'part': {'face': '#45B7D1', 'edge': '#0984E3', 'text': 'white'},      # Blue
            'division': {'face': '#FD79A8', 'edge': '#E84393', 'text': 'white'},  # Pink
            'subdivision': {'face': '#FDCB6E', 'edge': '#E17055', 'text': 'black'}, # Orange
            'section': {'face': '#6C5CE7', 'edge': '#5F3DC4', 'text': 'white'}    # Purple
        }
        
    def load_data(self):
        """Load JSON data from file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.tree_data = json.load(f)
            print("Data loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def is_leaf_node(self, node):
        """Check if node is a leaf (contains list with [name, code] format)"""
        return isinstance(node, list) and len(node) == 2 and isinstance(node[0], str)
    
    def determine_node_type(self, key, value, level, parent_type=None):
        """Determine the type of node based on its position in hierarchy"""
        if key == "To be continued ...":
            # Use the same type as parent to inherit color
            return parent_type if parent_type else 'section'
        elif self.is_leaf_node(value):
            return 'section'  # Leaf nodes are always sections (blue/purple)
        elif level == 0:
            return 'root'
        elif level == 1:
            return 'volume'
        elif level == 2:
            return 'part'
        elif level == 3:
            return 'division'
        elif level == 4:
            return 'subdivision'
        else:
            return 'section'  # Deeper levels are also sections
    
    def get_display_name(self, key, value):
        """Get the display name for a node"""
        if self.is_leaf_node(value):
            return value[0]  # Return only the name, not the code
        return key
    
    def apply_display_rule(self, items):
        """Apply the rule: show max 2 items, add '...' if more exist"""
        if len(items) <= 2:
            return items
        else:
            result = items[:2]
            result.append(("To be continued ...", "more_items"))
            return result
    
    def calculate_subtree_width(self, node, level=0):
        """Calculate the total width needed for a subtree"""
        if self.is_leaf_node(node):
            return 1
        
        if not isinstance(node, dict):
            return 1
        
        items = list(node.items())
        display_items = self.apply_display_rule(items)
        
        if level == 0:  # At leaf level, just count items
            return len(display_items) * self.min_horizontal_spacing
        
        total_width = 0
        for key, value in display_items:
            if key == "To be continued ...":
                total_width += self.min_horizontal_spacing
            elif self.is_leaf_node(value):
                total_width += self.min_horizontal_spacing
            elif isinstance(value, dict):
                child_width = self.calculate_subtree_width(value, level - 1)
                total_width += child_width
            else:
                total_width += self.min_horizontal_spacing
        
        return max(total_width, len(display_items) * self.min_horizontal_spacing)
    
    def calculate_tree_layout(self):
        """Calculate optimal layout for the entire tree"""
        if not self.tree_data:
            return []
        
        all_nodes = []
        
        # First, calculate the maximum depth
        max_depth = self.get_max_depth(self.tree_data)
        
        # Calculate positions level by level
        self.position_nodes_recursive(self.tree_data, 0, 0, 0, all_nodes, max_depth)
        
        return all_nodes
    
    def get_max_depth(self, node, current_depth=0):
        """Get the maximum depth of the tree"""
        if self.is_leaf_node(node):
            return current_depth
        
        if not isinstance(node, dict):
            return current_depth
        
        max_child_depth = current_depth
        for key, value in node.items():
            if self.is_leaf_node(value):
                max_child_depth = max(max_child_depth, current_depth + 1)
            elif isinstance(value, dict):
                child_depth = self.get_max_depth(value, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
            else:
                max_child_depth = max(max_child_depth, current_depth + 1)
        
        return max_child_depth
    
    def position_nodes_recursive(self, node, level, center_x, parent_x, all_nodes, max_depth, parent_y=None, parent_type=None):
        """Recursively position nodes with proper spacing"""
        if self.is_leaf_node(node):
            return center_x
        
        if not isinstance(node, dict):
            return center_x
        
        items = list(node.items())
        display_items = self.apply_display_rule(items)
        
        # Calculate y position
        y = -level * self.level_height
        if parent_y is None:
            parent_y = y + self.level_height
        
        # Determine the node type for children at this level
        child_node_type = None
        if level == 0:
            child_node_type = 'volume'
        elif level == 1:
            child_node_type = 'part'
        elif level == 2:
            child_node_type = 'division'
        elif level == 3:
            child_node_type = 'subdivision'
        else:
            child_node_type = 'section'
        
        # Calculate total width needed for all children
        child_widths = []
        for key, value in display_items:
            if key == "To be continued ...":
                width = self.min_horizontal_spacing
            elif self.is_leaf_node(value):
                width = self.min_horizontal_spacing
            elif isinstance(value, dict):
                width = self.calculate_subtree_width(value, max_depth - level - 1)
            else:
                width = self.min_horizontal_spacing
            child_widths.append(width)
        
        total_width = sum(child_widths)
        
        # Position children
        current_x = center_x - total_width / 2
        child_positions = []
        
        for i, ((key, value), width) in enumerate(zip(display_items, child_widths)):
            child_center_x = current_x + width / 2
            
            # Create node info
            if key == "To be continued ...":
                node_type = child_node_type  # Use the same type as siblings
            else:
                node_type = self.determine_node_type(key, value, level, child_node_type)
            
            display_name = self.get_display_name(key, value)
            
            node_info = {
                'name': display_name,
                'x': child_center_x,
                'y': y,
                'level': level,
                'type': node_type,
                'parent_x': parent_x if level > 0 else None,
                'parent_y': parent_y if level > 0 else None
            }
            
            all_nodes.append(node_info)
            child_positions.append((child_center_x, key, value))
            
            current_x += width
        
        # Recursively position children
        for child_x, key, value in child_positions:
            if key != "To be continued ..." and not self.is_leaf_node(value) and isinstance(value, dict):
                self.position_nodes_recursive(
                    value, level + 1, child_x, child_x, all_nodes, max_depth, y, child_node_type
                )
        
        return center_x
    
    def create_visualization(self, figsize=(30, 20)):
        """Create the enhanced tree visualization"""
        if not self.tree_data:
            print("No data loaded. Please run load_data() first.")
            return
        
        # Calculate all node positions
        all_positions = self.calculate_tree_layout()
        
        if not all_positions:
            print("No positions calculated.")
            return
        
        # Create the plot with larger figure size
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.ax.set_aspect('equal')
        
        # Draw connections first (so they appear behind boxes)
        for node in all_positions:
            if node['parent_x'] is not None:
                self.ax.plot([node['parent_x'], node['x']], 
                           [node['parent_y'], node['y']], 
                           'k-', linewidth=1.5, alpha=0.7)
        
        # Draw nodes
        for node in all_positions:
            self.draw_enhanced_node(node)
        
        # Set plot limits with proper margins
        if all_positions:
            x_coords = [node['x'] for node in all_positions]
            y_coords = [node['y'] for node in all_positions]
            
            x_margin = (max(x_coords) - min(x_coords)) * 0.1 + 2
            y_margin = 2
            
            self.ax.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
            self.ax.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
        
        self.ax.set_title('Migration Act 1958 - Tree Structure Visualization', 
                          fontsize=20, fontweight='bold', pad=30)
        self.ax.axis('off')
        
        # Add enhanced legend
        self.add_enhanced_legend()
        
        plt.tight_layout()
        return self.fig
    
    def draw_enhanced_node(self, node):
        """Draw a single node with enhanced styling"""
        x, y = node['x'], node['y']
        node_type = node['type']
        
        # Get colors for this node type
        colors = self.colors.get(node_type, self.colors['section'])
        
        # Adjust node size based on type
        width = self.node_width
        height = self.node_height
        
        if node_type == 'root':
            width *= 1.3
            height *= 1.2
        elif node_type == 'volume':
            width *= 1.2
            height *= 1.1
        
        # Create rounded rectangle with shadow effect
        shadow = FancyBboxPatch(
            (x - width/2 + 0.05, y - height/2 - 0.05),
            width, height,
            boxstyle="round,pad=0.1",
            facecolor='gray',
            alpha=0.3,
            zorder=1
        )
        self.ax.add_patch(shadow)
        
        # Main box
        box = FancyBboxPatch(
            (x - width/2, y - height/2),
            width, height,
            boxstyle="round,pad=0.1",
            facecolor=colors['face'],
            edgecolor=colors['edge'],
            linewidth=2,
            zorder=2
        )
        self.ax.add_patch(box)
        
        # Add text with automatic line wrapping to fit in box
        text = node['name']
        
        # Calculate available width for text (leave some padding)
        available_width = width * 0.9
        
        # Estimate characters per line based on font size and box width
        fontsize = {
            'root': 12,
            'volume': 10,
            'part': 9,
            'division': 8,
            'subdivision': 8,
            'section': 7
        }.get(node_type, 8)
        
        # Rough estimation: smaller font = more characters per line
        chars_per_line = max(15, int(available_width * 3.5 / fontsize))
        
        # Split text into lines that fit within the box
        if len(text) > chars_per_line:
            words = text.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= chars_per_line:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                    else:
                        # Single word is too long, truncate it
                        lines.append(word[:chars_per_line-3] + "...")
                        current_line = []
                        current_length = 0
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Limit to maximum 3 lines to prevent overflow
            text = '\n'.join(lines[:3])
            if len(lines) > 3:
                # Replace last line with truncated version
                last_line = lines[2]
                if len(last_line) > chars_per_line - 3:
                    last_line = last_line[:chars_per_line-3] + "..."
                lines_to_show = lines[:2] + [last_line + "..."]
                text = '\n'.join(lines_to_show)
        
        # Font size based on node type
        fontsize = {
            'root': 12,
            'volume': 10,
            'part': 9,
            'division': 8,
            'subdivision': 8,
            'section': 7
        }.get(node_type, 8)
        
        fontweight = 'bold' if node_type in ['root', 'volume'] else 'normal'
        
        self.ax.text(x, y, text, ha='center', va='center', 
                    fontsize=fontsize, fontweight=fontweight,
                    color=colors['text'], family='sans-serif',
                    zorder=3)
    
    def add_enhanced_legend(self):
        """Add an enhanced legend explaining the hierarchy and color coding"""
        legend_elements = [
            patches.Patch(color=self.colors['root']['face'], label='Root (Act)'),
            patches.Patch(color=self.colors['volume']['face'], label='Volume'),
            patches.Patch(color=self.colors['part']['face'], label='Part'),
            patches.Patch(color=self.colors['division']['face'], label='Division'),
            patches.Patch(color=self.colors['subdivision']['face'], label='Subdivision'),
            patches.Patch(color=self.colors['section']['face'], label='Section (Article)')
        ]
        
        self.ax.legend(handles=legend_elements, loc='upper left', 
                      bbox_to_anchor=(0.02, 0.98), fontsize=12,
                      title="Hierarchy Levels", title_fontsize=14)
    
    def save_visualization(self, filename='enhanced_tree_visualization.png', dpi=300):
        """Save the visualization to file"""
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                           facecolor='white', edgecolor='none',
                           pad_inches=0.5)
            print(f"Enhanced visualization saved as {filename}")
        else:
            print("No visualization to save. Create visualization first.")
    
    def show(self):
        """Display the visualization"""
        if self.fig:
            plt.show()
        else:
            print("No visualization to show. Create visualization first.")

# Usage example
def main():
    # Initialize the enhanced visualizer
    SEARCH_TREE_FILE_PATH = "json_search_tree/all_vol_search_tree.json"
    visualizer = EnhancedTreeVisualizer(SEARCH_TREE_FILE_PATH)
    
    # Load data
    if visualizer.load_data():
        # Create enhanced visualization with larger figure
        fig = visualizer.create_visualization(figsize=(40, 25))
        
        # Save the visualization
        visualizer.save_visualization('migration_act_enhanced_tree.png', dpi=200)
        
        # Show the visualization
        visualizer.show()
        
        print("\nVisualization complete!")
        print("- Different colors show the document hierarchy levels")
        print("- Purple nodes are the actual sections/articles (leaf nodes)")
        print("- 'To be continued...' nodes now have the same color as their siblings")
        print("- All leaf nodes are now properly displayed")
        
    else:
        print("Failed to load data. Please check the file path.")

if __name__ == "__main__":
    main()