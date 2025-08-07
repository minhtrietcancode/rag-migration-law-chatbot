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

# import searching database + generate search term function + embedding the search term function
from generate_search_term import generate_search_term_from_question
from search_database import initialize_chromadb, get_vector
from embed_search_term import initialize_embedding_model, embed_search_term_with_model

# Initialize the chromaDB and embedding model first, as these take a bunch of time
chromadb_collection = initialize_chromadb()
embedding_model = initialize_embedding_model()

