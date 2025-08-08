# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
MODEL_NAME = "deepseek/deepseek-chat-v3-0324:free"

# LLM Parameters
LLM_TEMPERATURE = 0.05
LLM_MAX_TOKENS = 30

# Database Paths
VECTOR_DATABASE_PATH = "vector_database"
COLLECTION_NAME = "my_collection"

# File Paths
SEARCH_TREE_PATH = "final_json_searching_material/final_search_tree_embed_id.json"
HASHMAP_PATH = "final_json_searching_material/final_hashmap.json"
MIGRATION_ACT_CONTENT_BASE = "Migration Act Content Pages Txt Format"

# Embedding Model
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# Search Parameters
DEFAULT_SEARCH_LIMIT = 5

# Content Keys
START_PAGE_KEY = "start_page"
END_PAGE_KEY = "end_page"

# Tree Structure
MIGRATION_ACT_ROOT = "Migration Act 1958"