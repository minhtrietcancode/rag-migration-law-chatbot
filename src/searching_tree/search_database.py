# --- Constants
VECTOR_DATABASE_PATH = "vector_database"
COLLECTION_NAME = "my_collection"

# --- Imports
from chromadb import PersistentClient
from chromadb.config import Settings
import numpy as np
import time

def initialize_chromadb():
    """
    Initialize ChromaDB client and collection once.
    
    Returns:
        collection: ChromaDB collection object, or None if failed
    """
    try:
        # Initialize ChromaDB client
        client = PersistentClient(
            path=VECTOR_DATABASE_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        start_time = time.time()
        # Get the collection
        collection = client.get_collection(COLLECTION_NAME)
        elapsed = time.time() - start_time
        print(f"✅ ChromaDB initialized successfully in {elapsed:.2f} seconds")
        return collection
        
    except Exception as e:
        print(f"❌ Failed to initialize ChromaDB: {str(e)}")
        return None

def get_vector(collection, tree_node):
    """
    Retrieve embedding vector for a tree node using pre-initialized collection.
    
    Args:
        collection: ChromaDB collection object from initialize_chromadb()
        tree_node (str): A string like "Short title_0" or "Commencement_1"
    
    Returns:
        numpy.ndarray: The embedding vector, or None if not found
    """
    if collection is None:
        print("❌ Collection is None. Make sure to initialize ChromaDB first.")
        return None
    
    # Extract the ID from the tree node
    node_id = tree_node.split("_")[-1]
    
    try:
        # Query for the specific ID
        results = collection.get(
            ids=[node_id],
            include=["embeddings"]
        )
        
        # Check if we found the ID
        if not results['ids'] or len(results['ids']) == 0:
            print(f"ID '{node_id}' not found in the database")
            return None
        
        # Extract and return the embedding vector
        embedding = results['embeddings'][0]
        return np.array(embedding)
        
    except Exception as e:
        print(f"Error retrieving embedding for node '{tree_node}': {str(e)}")
        return None

# --- Example usage, uncomment for testing
# if __name__ == "__main__":
#     # Step 1: Initialize once
#     print("🔧 Initializing ChromaDB...")
#     collection = initialize_chromadb()
    
#     if collection is not None:
#         # Step 2: Use for multiple retrievals
#         test_nodes = [
#             "Short title_1_Volume 1_1",
#             "Commencement_2_Volume 1_2",
#             "Repeal and savings_3_Volume 1_3",
#             "Act not to apply so as to exceed Commonwealth power_3A_Volume 1_4",
#             "Compensation for acquisition of property_3B_Volume 1_5",
#             "Object of Act_4_Volume 1_6",
#             "Detention of minors a last resort_4AA_Volume 1_7",
#             "Application of the Criminal Code_4A_Volume 1_8",
#             "Interpretation_5_Volume 1_9",
#             "Non-citizen’s responsibility in relation to protection claims_5AAA_Volume 1_10",
#             "Meaning of unauthorised maritime arrival_5AA_Volume 1_11",
#             "Sentencing for offences_5AB_Volume 1_12",
#             "Meaning of personal identifier_5A_Volume 1_13",
#             "When personal identifier taken not to have been provided_5B_Volume 1_14",
#             "Meaning of character concern_5C_Volume 1_15",
#             "Child of a person_5CA_Volume 1_16",
#             "De facto partner_5CB_Volume 1_17",
#             "Limiting the types of identification tests that authorised officers may carry out_5D_Volume 1_18",
#             "Meaning of purported privative clause decision_5E_Volume 1_19",
#             "Spouse_5F_Volume 1_20",
#             "Relationships and family members_5G_Volume 1_21",
#             "Meaning of refugee_5H_Volume 1_22",
#             "Meaning of well-founded fear of persecution_5J_Volume 1_23",
#             "Membership of a particular social group consisting of family_5K_Volume 1_24",
#             "Membership of a particular social group other than family_5L_Volume 1_25",
#             "Effective protection measures_5LA_Volume 1_26",
#             "Particularly serious crime_5M_Volume 1_27",
#             "Effect of limited meaning of enter Australia etc._6_Volume 1_28",
#             "Act to extend to certain Territories_7_Volume 1_29",
#             "Effect on executive power to protect Australia’s borders_7A_Volume 1_30",
#             "Certain resources installations to be part of Australia_8_Volume 1_31",
#             "Certain sea installations to be part of Australia_9_Volume 1_32",
#             "Migration zone etc.—offshore resources activities_9A_Volume 1_33",
#             "Certain children taken to enter Australia at birth_10_Volume 1_34",
#             "Visa applicable to 2 or more persons_11_Volume 1_35",
#             "When applications under this Act are finally determined_11A_Volume 1_36",
#             "Application of Part VA of the Marriage Act_12_Volume 1_37"
#         ]
        
#         print("\n🚀 Testing multiple retrievals...")
#         for node in test_nodes:
#             print(f"\nRetrieving: {node}")
#             vector = get_vector(collection, node)
            
#             if vector is not None:
#                 print(f"✅ Success! Shape: {vector.shape}, First 3 dims: {vector[:3]}")
#             else:
#                 print("❌ Failed to retrieve vector")
    
#     else:
#         print("❌ Cannot proceed - ChromaDB initialization failed")