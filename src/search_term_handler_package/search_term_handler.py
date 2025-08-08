# search_term_handler.py
import re
import time
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from sentence_transformers import SentenceTransformer
import config

class SearchTermHandler:
    """Handles search term generation and embedding"""
    
    def __init__(self):
        self.llm = None
        self.search_term_chain = None
        self.embedding_model = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM and prompt chain"""
        self.llm = ChatOpenAI(
            openai_api_key=config.OPENROUTER_API_KEY,
            openai_api_base=config.OPENROUTER_API_BASE,
            model=config.MODEL_NAME,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS
        )
        
        # Create the prompt template
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
        
        # Create the chain
        self.search_term_chain = prompt | self.llm
    
    def clean_search_term(self, raw_term: str) -> str:
        """Clean and validate the generated search term"""
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
    
    def generate_search_term(self, user_question: str) -> Optional[str]:
        """Generate clean search term from user question"""
        if not user_question or not user_question.strip():
            print("❌ Empty question provided")
            return None
        
        try:
            response = self.search_term_chain.invoke({"question": user_question})
            search_term = self.clean_search_term(response.content)
            
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
    
    def initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        start_model = time.time()
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        end_model = time.time()
        print(f"Model initialization took {end_model - start_model:.4f} seconds")
    
    def embed_search_term(self, search_term: str):
        """Embed a search term using the sentence transformer model"""
        if self.embedding_model is None:
            self.initialize_embedding_model()
        
        start_embed = time.time()
        embedding = self.embedding_model.encode(search_term)
        end_embed = time.time()
        print(f"Embedding took {end_embed - start_embed:.8f} seconds")
        return embedding