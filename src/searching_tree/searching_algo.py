''' 
    This piece of code is the place where everything run together. Recall the flow of searching again  
    + User input a question --> than handle and return search term for this question by 
      generate_search_term_from_question
    + Initialize the chromaDB first so that in the future we just need to use it, no need for 
      repeatedly initialization each time we search for a embedded vector of any node
    + We will then embed the generated search term from above 
    + And then we will conduct our searching algorithm on the tree, by calculating the cosine similarity / matching
      score for the embedded vector of search term, and the retrieved vector of a node <-- this would be done 
      by the get_vector function that will return the pre - embedded vector of a given node (a node is a string)
'''
# numpy for faster cosine similarity calculation
import numpy as np
from typing import Union, List, Dict, Any
import json

# import searching database + generate search term function + embedding the search term function
'''
    Remind about the function that we already got and are intending to use 
        + generate_search_term_from_question(user_question): this function would receive a question (string) from a user
          and then return a search term for that question (string)

        + initialize_chromadb(): this function would load and return a collection - chromadb that be used later 
          for searching vector of any tree node
        + initialize_embedding_model(): this function would load the sentence transformer - model all-miniLM-L6-V2 and then 
          return that model, which will be used later for embedding a given search term
        
        + get_vector(chromadb, tree_node): this function would take a chromadb - collection (which would be 
          initialized before) and then return the pre-embeded vector of the tree_node
        + embed_search_term_with_model(model, search_term): this function would take a pre-initialized model 
          (sentence transformer - all miniLM L6 V2) and then return the embedded vector of the search_term (which is a string)
'''
from generate_search_term import generate_search_term_from_question
from search_database import initialize_chromadb, get_vector
from embed_search_term import initialize_embedding_model, embed_search_term_with_model

# function to calculate cosine similarity between 2 embedded vectors 
def calculate_cosine_similarity(vector1: Union[np.ndarray, List[float]], 
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

# function to load the json file of the tree into a dictionary and return it
def load_search_tree():
    SEARCH_TREE_PATH = "final_json_searching_material/final_search_tree_embed_id.json"
    search_tree = {}
    # Load JSON
    with open(SEARCH_TREE_PATH, "r", encoding="utf-8") as f:
        search_tree = json.load(f)
    
    # return the loaded json in dictionary type
    return search_tree


def is_section(node_name: str) -> bool:
    """
    Check if a node is a section (leaf node) based on naming pattern.
    Sections typically have numbers and specific patterns.
    """
    # This might need adjustment based on your actual section naming patterns
    # For now, assuming sections are the ones that don't have children or have specific patterns
    return "_" in node_name and any(char.isdigit() for char in node_name)


def search_term_on_tree(search_tree: Dict[str, Any], 
                       search_term_vector: List[float], 
                       chromadb_collection,
                       limit: int = 5) -> List[str]:
    """
    Greedy search algorithm to find the most relevant sections.
    
    Args:
        search_tree: The loaded tree structure as dictionary
        search_term_vector: Embedded vector of the search term
        chromadb_collection: ChromaDB collection for getting node vectors
        limit: Maximum number of sections to return
    
    Returns:
        List[str]: List of section names that best match the search term
    """
    
    found_sections = []
    
    def greedy_dfs(current_node: Dict[str, Any], current_path: str = "", is_root: bool = False):
        """
        Recursive greedy depth-first search.
        """
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
                    child_vector = get_vector(chromadb_collection, child_name)
                    
                    # Calculate similarity with search term
                    similarity = calculate_cosine_similarity(search_term_vector, child_vector)
                    
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
                child_vector = get_vector(chromadb_collection, child_name)
                
                # Calculate similarity with search term
                similarity = calculate_cosine_similarity(search_term_vector, child_vector)
                
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
    
    # Start the search from the Migration Act 1958 root (skip similarity calculation for root)
    if "Migration Act 1958" in search_tree:
        greedy_dfs(search_tree["Migration Act 1958"], is_root=True)
    
    return found_sections[:limit]


# Testing the function
def test_greedy_search():
    """
    Test function for the greedy search algorithm
    """
    print("=== Testing Greedy Search Algorithm ===")
    
    # Initialize the chromaDB and embedding model
    print("Initializing ChromaDB and embedding model...")
    chromadb_collection = initialize_chromadb()
    embedding_model = initialize_embedding_model()
    
    # Load the search tree
    print("Loading search tree...")
    search_tree = load_search_tree()
    
    # Sample search term (avoiding LLM call to save tokens)
    sample_search_term = "working visa"
    print(f"Search term: {sample_search_term}")
    
    # Embed the search term
    print("Embedding search term...")
    search_term_vector = embed_search_term_with_model(embedding_model, sample_search_term)
    
    # Perform the greedy search
    print("Starting greedy search...")
    results = search_term_on_tree(
        search_tree=search_tree,
        search_term_vector=search_term_vector,
        chromadb_collection=chromadb_collection,
        limit=5
    )
    
    # Display results
    print("\n=== SEARCH RESULTS ===")
    print(f"Found {len(results)} sections:")
    for i, section in enumerate(results, 1):
        print(f"{i}. {section}")
    
    return results


# Uncomment to run the test
if __name__ == "__main__":
    test_results = test_greedy_search()