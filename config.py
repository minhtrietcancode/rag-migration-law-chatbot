# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

###############################################################################################################
'''
    LLM API key + configuration setup 
'''
# load api key + configure model + url 
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "qwen/qwen2.5-vl-32b-instruct:free"

# LLM Parameters
LLM_TEMPERATURE = 0.05
LLM_MAX_TOKENS = 30


###############################################################################################################
'''
    Token key + configuration setup for embedding the seacrch term via API call with
    third party - Hugging Face
'''
# HF token for embedding via API call with third party
HF_TOKEN = os.getenv("HF_TOKEN")

# APU url
API_URL = (
    "https://router.huggingface.co/"
    "hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
)

# confugure header
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}


###############################################################################################################
'''
    Constants path for the things we will use during searching 
        + Path for vector database when need retreiving the pre embedded vector 
        + JSON file for searching + hashing
'''
# Database Paths
VECTOR_DATABASE_PATH = "vector_database"
COLLECTION_NAME = "my_collection"

# File Paths
SEARCH_TREE_PATH = "final_json_searching_material/final_search_tree_embed_id.json"
HASHMAP_PATH = "final_json_searching_material/final_hashmap.json"
MIGRATION_ACT_CONTENT_BASE = "Migration Act Content Pages Txt Format"

# Search Parameters
DEFAULT_SEARCH_LIMIT = 5

# Content Keys
START_PAGE_KEY = "start_page"
END_PAGE_KEY = "end_page"

# Tree Structure
MIGRATION_ACT_ROOT = "Migration Act 1958"


###############################################################################################################