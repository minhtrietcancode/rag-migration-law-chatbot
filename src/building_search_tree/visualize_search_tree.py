import matplotlib.pyplot as plt

# For image annotation
from PIL import Image, ImageDraw, ImageFont
def add_note_to_image(image_path):
    """
    Add a small, semi-transparent note at the top-left of the image at image_path.
    The note is: 'Note: This is an overview, the number of children for each node depends on actual contents'
    """
    note = "Note: This is an overview, the number of children for each node depends on actual contents"
    try:
        img = Image.open(image_path).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (255,255,255,0))
        draw = ImageDraw.Draw(overlay)
        # Try to use a common font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 49)
        except:
            font = ImageFont.load_default()
        # Set position and color (semi-transparent black)
        x, y = 20, 20
        text_color = (0, 0, 0, 120)  # semi-transparent black
        # Draw text (not bold)
        draw.text((x, y), note, font=font, fill=text_color)
        # Composite overlay onto image
        out = Image.alpha_composite(img, overlay)
        # Save back (overwrite)
        out = out.convert("RGB")
        out.save(image_path)
        print(f"Note added to {image_path}")
    except Exception as e:
        print(f"Failed to add note: {e}")

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
MAX_CHILDREN        = 2    # max children for levels < LEAF_PARENT_LEVEL
LEAF_PARENT_LEVEL   = 4    # one level above leaves
MAX_LEAF_PER_PARENT = 1    # how many leaves to show per subdivision
OUTPUT_PATH         = 'json_search_tree/migration_act_search_tree.png'

# -------------------------------------------------------------------
# TREE DATA STRUCTURE
# -------------------------------------------------------------------
class TreeNode:
    def __init__(self, name, level=0):
        self.name     = name
        self.level    = level
        self.children = []
        self.x = self.y = 0

    def add_child(self, child):
        child.level = self.level + 1
        self.children.append(child)

def create_migration_act_tree():
    root = TreeNode("Migration Act 1958", 0)
    # Volumes keep their numbers
    for i in (1, 2):
        vol = TreeNode(f"Volume {i}", 1)
        root.add_child(vol)

        # All deeper nodes drop their numbers
        for part_idx in range(1, 5):
            part_label = "Part" if part_idx <= 3 else "To be continued..."
            part = TreeNode(part_label, 2)
            vol.add_child(part)

            if part_idx <= 3:
                for div_idx in range(1, 5):
                    div_label = "Division" if div_idx <= 3 else "To be continued..."
                    div = TreeNode(div_label, 3)
                    part.add_child(div)

                    if div_idx <= 3:
                        for sub_idx in range(1, 5):
                            sub_label = "Subdivision" if sub_idx <= 3 else "To be continued..."
                            sub = TreeNode(sub_label, 4)
                            div.add_child(sub)

                            if sub_idx <= 3:
                                for sec_idx in range(1, 5):
                                    sec_label = "Section" if sec_idx <= 3 else "To be continued..."
                                    sec = TreeNode(sec_label, 5)
                                    sub.add_child(sec)

    return root

# -------------------------------------------------------------------
# HELPERS TO SLICE CHILDREN
# -------------------------------------------------------------------
def get_display_children(node):
    if node.level == LEAF_PARENT_LEVEL:
        return node.children[:MAX_LEAF_PER_PARENT]
    return node.children[:MAX_CHILDREN]

# -------------------------------------------------------------------
# LAYOUT CALCULATIONS
# -------------------------------------------------------------------
def calculate_positions(node, x=0, y=0, level_spacing=3, node_spacing=2):
    kids = get_display_children(node)
    if not kids:
        node.x, node.y = x, y
        return 1

    widths = []
    total = 0
    for ch in kids:
        w = calculate_positions(ch, 0, y - level_spacing, level_spacing, node_spacing)
        widths.append(w)
        total += w
    total += (len(kids) - 1) * node_spacing

    start = x - total / 2
    for w, ch in zip(widths, kids):
        center = start + w / 2
        shift_subtree(ch, center - ch.x)
        start += w + node_spacing

    node.x, node.y = x, y
    return total

def shift_subtree(node, dx):
    node.x += dx
    for c in node.children:
        shift_subtree(c, dx)

# -------------------------------------------------------------------
# DRAWING
# -------------------------------------------------------------------
def get_node_color(level):
    palette = ['#FF6B6B','#4ECDC4','#45B7D1','#96CEB4','#FFEAA7','#DDA0DD']
    return palette[level % len(palette)]

def draw_tree(root):
    calculate_positions(root)

    fig, ax = plt.subplots(figsize=(20,16))
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('#f8f9fa')

    # collect nodes
    all_nodes = []
    def collect(n):
        all_nodes.append(n)
        for c in get_display_children(n):
            collect(c)
    collect(root)

    # set bounds
    min_x = min(n.x for n in all_nodes) - 2
    max_x = max(n.x for n in all_nodes) + 2
    min_y = min(n.y for n in all_nodes) - 1
    max_y = max(n.y for n in all_nodes) + 1
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)

    # draw connections
    def draw_conn(n):
        for c in get_display_children(n):
            ax.plot([n.x, c.x], [n.y-0.3, c.y+0.3], 'k-', lw=2, alpha=0.6, zorder=1)
            draw_conn(c)
    draw_conn(root)

    # draw nodes with auto-sizing bbox
    def draw_node(n):
        ax.text(
            n.x, n.y, n.name,
            ha='center', va='center',
            fontsize=9, fontweight='bold',
            color='black',
            bbox=dict(
                boxstyle='round,pad=0.3',
                facecolor=get_node_color(n.level),
                edgecolor='k',
                linewidth=2
            ),
            zorder=3
        )
        for c in get_display_children(n):
            draw_node(c)

    draw_node(root)

    # legend
    labels = ['Act','Volume','Part','Division','Subdivision','Section']
    patches = [plt.Rectangle((0,0),1,1,facecolor=get_node_color(i)) for i in range(len(labels))]
    ax.legend(
        patches,
        labels,
        loc='upper right',
        bbox_to_anchor=(1.05, 1),    # moved legend closer to the plot
        fontsize=10
    )
    ax.set_title('Migration Act 1958',
                 fontsize=18, fontweight='bold', pad=20)

    # trim unused white space and adjust padding
    plt.tight_layout(pad=1)
    fig.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches='tight',        # crop to content
        pad_inches=0.1              # small padding around
    )
    print(f"Saved updated tree to {OUTPUT_PATH}")
    add_note_to_image(OUTPUT_PATH)

# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    root = create_migration_act_tree()
    draw_tree(root)
