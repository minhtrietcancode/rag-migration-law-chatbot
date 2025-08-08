import os
import re
from typing import Optional, List, Union, List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from sentence_transformers import SentenceTransformer
import time
import numpy as np
import json

##########################################################################################################################################
                            # CODE FOR GENERATE SEARCH TERM FROM USER QUESTION
##########################################################################################################################################
# Load API key
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Set up the ChatOpenAI client with optimized parameters
llm = ChatOpenAI(
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    model="deepseek/deepseek-chat-v3-0324:free",
    temperature=0.05,  # Lower for more consistent legal terminology
    max_tokens=30      # Reduced since we only need 2-4 words
)

# Optimized prompt for embedding-based similarity search
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     """You are a Migration Act search term generator. Generate a focused 2-3 word term for embedding-based similarity search of Australian Migration Act sections.

CRITICAL: Generate ONE focused concept that will match well with Migration Act node descriptions through semantic similarity.

Your terms will be embedded and compared via cosine similarity with nodes like:
- "Arrival, presence and departure of persons"
- "Migration agents and immigration assistance"  
- "Reviewable migration decisions and reviewable protection decisions"
- "Judicial review"
- "Restrictions on court proceedings"

GENERATE focused terms that represent the CORE legal concept:

"What do I need to study abroad?" → "student visa"
"Can I work while visiting Australia?" → "visitor work rights"  
"What happens if I overstay my tourist visa?" → "visa overstay"
"How to bring my wife to Australia?" → "partner visa" 
"Can refugees get visas here?" → "protection visa"
"What if my application gets rejected?" → "visa refusal"
"Can I stay while waiting for decision?" → "bridging visa"
"What are the health checks needed?" → "health requirements"
"Can criminals get Australian visas?" → "character requirements"
"How do I appeal a decision?" → "judicial review"
"What about court restrictions?" → "court proceedings"

AVOID:
- Multiple concepts in one term
- Repetitive words like "visa visa visa"  
- Long descriptive phrases
- Generic terms

Generate ONE clear concept that embeddings can match semantically.

Return ONLY the search terms, no quotes, no explanations."""
    ),
    ("user", "{question}")
])

# Create the LLM chain using modern syntax
search_term_chain = prompt | llm

# No fallback system - we want to know when LLM fails

def clean_search_term(raw_term: str) -> str:
    """
    Clean and validate the generated search term.
    """
    if not raw_term:
        return ""
    
    # Remove quotes, extra whitespace, and newlines
    cleaned = re.sub(r'["\'\n\r]', '', raw_term.strip())
    
    # Take only the first line if multiple lines
    cleaned = cleaned.split('\n')[0].strip()
    
    # Remove common prefixes that might be added
    prefixes_to_remove = [
        'search term:', 'search terms:', 'term:', 'terms:',
        'key terms:', 'keywords:', 'search for:', 'look for:'
    ]
    
    for prefix in prefixes_to_remove:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    
    # Limit to reasonable length (2-6 words)
    words = cleaned.split()
    if len(words) > 6:
        cleaned = ' '.join(words[:6])
    
    return cleaned

def generate_search_term_from_question(user_question: str) -> Optional[str]:
    """
    Generate clean search term from user question using LangChain.
    
    Args:
        user_question: The user's question about Migration Act
        
    Returns:
        Clean search term string, or None if generation fails
    """
    if not user_question or not user_question.strip():
        print("❌ Empty question provided")
        return None
    
    try:
        # Use modern invoke method instead of deprecated run
        response = search_term_chain.invoke({"question": user_question})
        search_term = clean_search_term(response.content)
        
        # Validate the result
        if search_term and len(search_term.split()) >= 1:
            print(f"🔍 Generated search term: '{search_term}' from question: '{user_question[:50]}...'")
            return search_term
        else:
            print(f"❌ LLM returned empty or invalid result: '{search_term}' for question: '{user_question[:50]}...'")
            return None
            
    except Exception as e:
        print(f"❌ System failed to generate search term: {str(e)} for question: '{user_question[:50]}...'")
        return None


##########################################################################################################################################
                                # CODE FOR SEARCHING DATABASE OF PRE EMBEDDED VECTOR OF A TREE NODE
##########################################################################################################################################
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
        print(f"✅ ChromaDB initialized successfully in {elapsed:.8f} seconds")
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


##########################################################################################################################################
                                        # CODE FOR EMBEDDING THE SEARCH TERM 
##########################################################################################################################################
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
    print(f"Embedding took {end_embed - start_embed:.8f} seconds")
    return embedding


##########################################################################################################################################
                                # CODE FOR SEARCHING A TERM ON THE TREE - GREEDY APPROACH
##########################################################################################################################################
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
    sample_search_term = "violation penalty"
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


##########################################################################################################################################
                                # CODE FOR GETTING THE PAGES OF THE RETURNED LIST OF SECTIONS 
##########################################################################################################################################
def load_hashmap_section_page():
    HASHMAP_PATH = "final_json_searching_material/final_hashmap.json"
    hashmap = {}
    # Load JSON
    with open(HASHMAP_PATH, "r", encoding="utf-8") as f:
        hashmap = json.load(f)
    
    # return the loaded json in dictionary type
    return hashmap

def get_start_end_page(hashmap, section_name_on_search_tree):
    START_PAGE_KEY = "start_page"
    END_PAGE_KEY = "end_page"
    # firstly convert the section name on tree node --> correct format in hashmap
    normalized_section_name = "_".join(section_name_on_search_tree.split("_")[:-1])

    # get the start and end pages
    start_page = hashmap[normalized_section_name][START_PAGE_KEY]
    end_page = hashmap[normalized_section_name][END_PAGE_KEY]

    # return a tuple with first element as start page, second element as end page
    return (start_page, end_page)

def extract_section_code(section_name_on_search_tree):
    SECTION_CODE_INDEX_ON_SEARCH_TREE = 1
    return section_name_on_search_tree.split("_")[SECTION_CODE_INDEX_ON_SEARCH_TREE]

def extract_section_vol(section_name_on_search_tree):
    SECTION_VOL_INDEX_ON_SEARCH_TREE = 2
    return section_name_on_search_tree.split("_")[SECTION_VOL_INDEX_ON_SEARCH_TREE]

def get_directory_relative_path_section(section_name_on_search_tree):
    vol_number = extract_section_vol(section_name_on_search_tree)[-1]

    # get relative path - vol 1 or vol 2
    relative_path = "Migration Act Content Pages Txt Format/volume " + vol_number

    # return that relative path
    return relative_path

def get_all_pages_content(hashmap, section_name_on_search_tree):
    # firstly get the directory path first 
    directory_path = get_directory_relative_path_section(section_name_on_search_tree)

    # then get the pages we need to loop through 
    (start_page, end_page) = get_start_end_page(hashmap, section_name_on_search_tree)

    # setup list of output path
    all_content = ""
    DEBUG_LINE = "=" * 80
    NEW_LINE_CHAR = "\n"

    # get the section code and vol number
    section_code = extract_section_code(section_name_on_search_tree)
    vol_num = extract_section_vol(section_name_on_search_tree)

    # add some debug few lines for displayed content
    all_content += DEBUG_LINE + NEW_LINE_CHAR
    all_content += f"From Page {start_page} to {end_page} of {vol_num}, Section {section_code}\n"
    all_content += DEBUG_LINE + NEW_LINE_CHAR

    # then loops through the start page until hit the end page
    for page in range(start_page, end_page + 1):
        current_page_path = directory_path + "/" + "page_" + str(page) + ".txt"
        with open(current_page_path, "r", encoding="utf-8") as file:
            content = file.read()
            all_content += content + NEW_LINE_CHAR

    # return the formatted pages
    return all_content

# testing
sample_section_name_on_search_tree = 'Migration Agents Registration Authority to give client documents to clients_306K_Volume 2_779'
hashmap = load_hashmap_section_page()
print(get_all_pages_content(hashmap, sample_section_name_on_search_tree))