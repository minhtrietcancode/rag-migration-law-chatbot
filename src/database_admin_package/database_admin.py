# database_admin.py
import time
import numpy as np
from chromadb import PersistentClient
from chromadb.config import Settings
import config

class DatabaseAdmin:
    """Handles ChromaDB operations and vector retrieval"""
    
    def __init__(self):
        self.client = None
        self.collection = None
    
    def initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client
            self.client = PersistentClient(
                path=config.VECTOR_DATABASE_PATH,
                settings=Settings(anonymized_telemetry=False)
            )
            
            start_time = time.time()
            # Get the collection
            self.collection = self.client.get_collection(config.COLLECTION_NAME)
            elapsed = time.time() - start_time
            print(f"✅ ChromaDB initialized successfully in {elapsed:.8f} seconds")
            return self.collection
            
        except Exception as e:
            print(f"❌ Failed to initialize ChromaDB: {str(e)}")
            return None
    
    def get_vector(self, tree_node: str):
        """
        Retrieve embedding vector for a tree node.
        
        Args:
            tree_node (str): A string like "Short title_0" or "Commencement_1"
        
        Returns:
            numpy.ndarray: The embedding vector, or None if not found
        """
        if self.collection is None:
            print("❌ Collection is None. Make sure to initialize ChromaDB first.")
            return None
        
        # Extract the ID from the tree node
        node_id = tree_node.split("_")[-1]
        
        try:
            # Query for the specific ID
            results = self.collection.get(
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