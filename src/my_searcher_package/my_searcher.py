# my_searcher.py
import json
import numpy as np
from typing import Dict, Any, List, Union
import sys
sys.path.append('./')
import config

class MySearcher:
    """Handles search tree operations and greedy search algorithm"""
    
    def __init__(self):
        self.search_tree = None
    
    def load_search_tree(self):
        """Load the search tree from JSON file"""
        try:
            with open(config.SEARCH_TREE_PATH, "r", encoding="utf-8") as f:
                self.search_tree = json.load(f)
            print("✅ Search tree loaded successfully")
            return self.search_tree
        except Exception as e:
            print(f"❌ Failed to load search tree: {str(e)}")
            return None
    
    def calculate_cosine_similarity(self, vector1: Union[np.ndarray, List[float]], 
                                  vector2: Union[np.ndarray, List[float]]) -> float:
        """
        Calculate cosine similarity between two embedded vectors.
        
        Args:
            vector1: First embedding vector (numpy array or list)
            vector2: Second embedding vector (numpy array or list)
        
        Returns:
            float: Cosine similarity score between -1 and 1
                   1 = identical vectors
                   0 = orthogonal vectors  
                  -1 = opposite vectors
        
        Raises:
            ValueError: If vectors have different dimensions or are zero vectors
        """
        # Convert to numpy arrays if they aren't already
        v1 = np.array(vector1)
        v2 = np.array(vector2)
        
        # Check if vectors have same dimensions
        if v1.shape != v2.shape:
            raise ValueError(f"Vectors must have same dimensions. Got {v1.shape} and {v2.shape}")
        
        # Calculate dot product
        dot_product = np.dot(v1, v2)
        
        # Calculate magnitudes (L2 norms)
        magnitude1 = np.linalg.norm(v1)
        magnitude2 = np.linalg.norm(v2)
        
        # Check for zero vectors
        if magnitude1 == 0 or magnitude2 == 0:
            raise ValueError("Cannot calculate cosine similarity with zero vectors")
        
        # Calculate cosine similarity
        similarity = dot_product / (magnitude1 * magnitude2)
        
        return float(similarity)
    
    def search_term_on_tree(self, search_term_vector: List[float], 
                           database_admin, limit: int = None) -> List[str]:
        """
        Greedy search algorithm to find the most relevant sections.
        
        Args:
            search_term_vector: Embedded vector of the search term
            database_admin: DatabaseAdmin instance for getting node vectors
            limit: Maximum number of sections to return
        
        Returns:
            List[str]: List of section names that best match the search term
        """
        if limit is None:
            limit = config.DEFAULT_SEARCH_LIMIT
        
        if self.search_tree is None:
            self.load_search_tree()
        
        found_sections = []
        
        def greedy_dfs(current_node: Dict[str, Any], current_path: str = "", is_root: bool = False):
            """Recursive greedy depth-first search"""
            nonlocal found_sections
            
            # If we've reached the limit, stop searching
            if len(found_sections) >= limit:
                return
                
            # If current node has no children, it's a leaf (section)
            if not current_node or len(current_node) == 0:
                return
                
            # For root level, calculate similarity but don't embed the root itself
            if is_root:
                print("Starting from root level - calculating similarity for parts...")
                child_scores = []
                
                # Calculate similarity for all parts (children of root)
                for child_name, child_content in current_node.items():
                    try:
                        # Get the embedded vector for this part
                        child_vector = database_admin.get_vector(child_name)
                        
                        # Calculate similarity with search term
                        similarity = self.calculate_cosine_similarity(search_term_vector, child_vector)
                        
                        child_scores.append((child_name, child_content, similarity))
                        print(f"Part: {child_name} (similarity: {similarity:.4f})")
                        
                    except Exception as e:
                        print(f"Error processing part {child_name}: {e}")
                        continue
                
                # Sort by similarity score (descending)
                child_scores.sort(key=lambda x: x[2], reverse=True)
                
                if not child_scores:
                    print("No valid parts found!")
                    return
                    
                # Greedy: Choose only the best part
                best_part_name, best_part_content, best_similarity = child_scores[0]
                print(f"🎯 CHOOSING BEST PART: {best_part_name} (similarity: {best_similarity:.4f})")
                
                # Check if this part contains sections (list of section names)
                if isinstance(best_part_content, list) and len(best_part_content) > 0:
                    # This part contains a list of sections - collect them!
                    print(f"✅ Found {len(best_part_content)} sections in part: {best_part_name}")
                    for section_name in best_part_content:
                        if len(found_sections) >= limit:
                            break
                        found_sections.append(section_name)
                        print(f"  ✅ Collected section: {section_name}")
                elif isinstance(best_part_content, list) and len(best_part_content) == 0:
                    # Empty list - this part itself is a section
                    found_sections.append(best_part_name)
                    print(f"✅ Found section at part level: {best_part_name}")
                elif isinstance(best_part_content, dict) and len(best_part_content) == 0:
                    # Empty dict - this part itself is a section  
                    found_sections.append(best_part_name)
                    print(f"✅ Found section at part level: {best_part_name}")
                elif isinstance(best_part_content, dict):
                    # Continue deeper with the best part
                    greedy_dfs(best_part_content, current_path + "/" + best_part_name, is_root=False)
                
                return
                
            # For non-root levels, calculate similarity scores
            print(f"Calculating similarity for children at level: {current_path}")
            child_scores = []
            
            for child_name, child_content in current_node.items():
                try:
                    # Get the embedded vector for this child node
                    child_vector = database_admin.get_vector(child_name)
                    
                    # Calculate similarity with search term
                    similarity = self.calculate_cosine_similarity(search_term_vector, child_vector)
                    
                    child_scores.append((child_name, child_content, similarity))
                    print(f"  - {child_name} (similarity: {similarity:.4f})")
                    
                except Exception as e:
                    print(f"Error processing child {child_name}: {e}")
                    continue
            
            if not child_scores:
                print("No valid children found at this level!")
                return
            
            # Sort by similarity score (descending)
            child_scores.sort(key=lambda x: x[2], reverse=True)
            
            # Greedy: Choose only the best child
            best_child_name, best_child_content, best_similarity = child_scores[0]
            print(f"🎯 CHOOSING: {best_child_name} to go deeper (similarity: {best_similarity:.4f})")
            
            # Check if this child contains sections (list of section names)
            if isinstance(best_child_content, list) and len(best_child_content) > 0:
                # This child contains a list of sections - collect them!
                print(f"✅ Found {len(best_child_content)} sections in: {best_child_name}")
                for section_name in best_child_content:
                    if len(found_sections) >= limit:
                        break
                    found_sections.append(section_name)
                    print(f"  ✅ Collected section: {section_name}")
                    
            elif isinstance(best_child_content, list) and len(best_child_content) == 0:
                # Empty list - this child itself is a section
                found_sections.append(best_child_name)
                print(f"✅ Found section: {best_child_name}")
                
            elif isinstance(best_child_content, dict) and len(best_child_content) == 0:
                # Empty dict - this child itself is a section
                found_sections.append(best_child_name)
                print(f"✅ Found section: {best_child_name}")
                
            elif isinstance(best_child_content, dict):
                # This has children, so continue deeper (greedy: only follow the best path)
                greedy_dfs(best_child_content, current_path + "/" + best_child_name, is_root=False)
        
        # Start the search from the Migration Act 1958 root
        if config.MIGRATION_ACT_ROOT in self.search_tree:
            greedy_dfs(self.search_tree[config.MIGRATION_ACT_ROOT], is_root=True)
        
        return found_sections[:limit]