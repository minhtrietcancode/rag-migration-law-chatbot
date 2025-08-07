from sentence_transformers import SentenceTransformer
import time

# Function to embed a search term - which is simply a string, using 
# sentence transformer - model: all-MiniLM-L6-v2 and return that embedded vector
def initialize_embedding_model():
    start_model = time.time()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    end_model = time.time()
    print(f"Model initialization took {end_model - start_model:.4f} seconds")
    return model

def embed_search_term_with_model(model, search_term: str):
    start_embed = time.time()
    embedding = model.encode(search_term)
    end_embed = time.time()
    print(f"Embedding took {end_embed - start_embed:.4f} seconds")
    return embedding

# Testing the embed search term function, uncomment for testing if needed 
# sample_search_term = "visa cancellations"
# model = initialize_embedding_model()
# vector = embed_search_term_with_model(model, sample_search_term)

# print("=" * 100)
# print(type(vector))


