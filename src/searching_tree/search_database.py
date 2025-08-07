# --- Constants
VECTOR_DATABASE_PATH = "vector_database"
COLLECTION_NAME = "my_collection"

# --- Imports (if not already imported)
from chromadb import PersistentClient
from chromadb.config import Settings
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

def get_embedded_vector_of_node(tree_node):
    """
    Get the embedded vector for a given tree node.
    
    Args:
        tree_node (str): A string like "Short title_0" or "Commencement_1"
    
    Returns:
        numpy.ndarray: The embedding vector, or None if not found
    """
    # Extract the ID from the tree node
    node_id = tree_node.split("_")[-1]
    
    try:
        # Initialize ChromaDB client
        client = PersistentClient(
            path=VECTOR_DATABASE_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get the collection
        collection = client.get_collection(COLLECTION_NAME)
        
        # Query for the specific ID
        results = collection.get(
            ids=[node_id],
            include=["embeddings", "documents"]  # Include both embeddings and documents
        )
        
        # Check if we found the ID
        if not results['ids'] or len(results['ids']) == 0:
            print(f"ID '{node_id}' not found in the database")
            return None
        
        # Extract the embedding vector
        embedding = results['embeddings'][0]  # Get the first (and should be only) result
        document = results['documents'][0] if results['documents'] else None
        
        print(f"Found embedding for ID '{node_id}': {document}")
        print(f"Embedding shape: {np.array(embedding).shape}")
        
        return np.array(embedding)
        
    except Exception as e:
        print(f"Error retrieving embedding for node '{tree_node}': {str(e)}")
        return None

# --- Example usage
if __name__ == "__main__":
    # Test the function
    test_node = "Non-citizen’s responsibility in relation to protection claims_5AAA_Volume 1_10"
    vector = get_embedded_vector_of_node(test_node)
    
    if vector is not None:
        print(f"Successfully retrieved vector with shape: {vector.shape}")
        print(f"First 5 dimensions: {vector[:5]}")
    else:
        print("Failed to retrieve vector")
        
    print("\n" + "="*80)
    print("🧪 TESTING: RE-EMBEDDING AND COMPARING WITH RETRIEVED VECTOR")
    print("="*80)
    
    # --- RE-EMBED THE SAME TEXT MANUALLY ---
    print("Step 1: Setting up the same model used for original embedding...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    print(f"Using device: {device}")
    
    # Extract the text part (same as extract_text_for_embed function)
    text_to_embed = test_node.split("_")[0]
    print(f"Step 2: Extracted text to embed: '{text_to_embed}'")
    
    # Manual embedding
    print("Step 3: Creating fresh embedding of the same text...")
    fresh_embedding = model.encode([text_to_embed], convert_to_numpy=True)[0]
    print(f"Fresh embedding shape: {fresh_embedding.shape}")
    
    if vector is not None:
        print("\nStep 4: Comparing retrieved vs fresh embeddings...")
        
        # --- COMPARISON ---
        # Cosine similarity
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        similarity = cosine_similarity(vector, fresh_embedding)
        
        # Check if nearly identical (allowing for tiny floating point differences)
        are_identical = np.allclose(vector, fresh_embedding, rtol=1e-6, atol=1e-9)
        
        # Detailed comparison
        print(f"📊 COMPARISON RESULTS:")
        print(f"   Cosine similarity: {similarity:.10f}")
        print(f"   Vectors identical (within tolerance): {are_identical}")
        print(f"   Max difference: {np.max(np.abs(vector - fresh_embedding)):.2e}")
        print(f"   Mean difference: {np.mean(np.abs(vector - fresh_embedding)):.2e}")
        
        # Show sample dimensions
        print(f"\n📋 SAMPLE DIMENSIONS COMPARISON:")
        print(f"   Retrieved[0:5]: {vector[:5]}")
        print(f"   Fresh[0:5]:     {fresh_embedding[:5]}")
        print(f"   Difference:     {vector[:5] - fresh_embedding[:5]}")
        
        # Final verdict
        print(f"\n🏆 FINAL VERDICT:")
        if similarity > 0.99999 and are_identical:
            print("   ✅ PERFECT MATCH! Embedding retrieval is 100% correct.")
        elif similarity > 0.999:
            print("   ✅ EXCELLENT MATCH! Minor floating point differences (normal).")
        elif similarity > 0.99:
            print("   ⚠️  GOOD MATCH but some differences detected.")
        else:
            print("   ❌ POOR MATCH! Something is wrong with the retrieval.")
    else:
        print("❌ Cannot compare - retrieval failed!")
    
    print("="*80)