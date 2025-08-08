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
from typing import Union, List

# import searching database + generate search term function + embedding the search term function
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

# testing the function

# Initialize the chromaDB and embedding model first, as these take a bunch of time
chromadb_collection = initialize_chromadb()
embedding_model = initialize_embedding_model()

# a sample node in the tree --> also get it pre embedded vector 
sample_node = "Visas for non-citizens_54"
sample_node_vector = get_vector(chromadb_collection, sample_node)

# a sample question --> generate search term --> embed that search term 
sample_question = "give me information about visa for non citizen people"
sample_search_term = generate_search_term_from_question(sample_question)
print("The search term is " + sample_search_term)
sample_search_term_vector = embed_search_term_with_model(embedding_model, sample_search_term)

# Calculate similarity 
cos_similarity = calculate_cosine_similarity(sample_node_vector, sample_search_term_vector)
print("Similarity is :", cos_similarity)

