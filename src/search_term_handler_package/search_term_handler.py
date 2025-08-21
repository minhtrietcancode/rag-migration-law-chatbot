# search_term_handler.py
import re
import time
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import sys
sys.path.append('./')
import config
from search_term_handler_package.embed_search_term_via_api import get_embedding


class SearchTermHandler:
    """Handles search term generation and embedding"""
    
    def __init__(self):
        self.llm = None
        self.search_term_chain = None
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
             """You are a Migration Act search-term generator used to produce ONE narrow search phrase for embedding-based similarity search of the Migration Act 1958 tree.

OBJECTIVE
- Return EXACTLY ONE short noun or noun-phrase (prefer 1–2 words; allow up to 3 only if necessary) that best captures the core legal concept in the user's question and will semantically match node titles/labels in the Migration Act search tree.

PRIORITY (follow in order)
1. If the user's question contains or clearly maps to an exact node label from the Migration Act tree, output that exact node label (wording and order) in lowercase.
2. Otherwise, output a close, concise synonym that maximizes semantic overlap with typical node labels (e.g., "bridging visa", "protection visa", "visa cancellation", "deportation", "ART review", "sponsorship obligations").
3. If multiple concepts are possible, choose the single most specific concept — do NOT combine concepts.

FORMAT RULES (must follow strictly)
- Output only the single search term. No explanation, no punctuation, no quotes, no extra lines.
- Use lowercase only, no leading/trailing whitespace.
- Use only letters, numbers, spaces and hyphens (avoid other punctuation).
- 1–3 words maximum; prefer 1–2 words.
- Prefer noun or noun-phrase (not full sentences or questions).
- Avoid generic umbrella terms like "immigration" or "visa issues". Prefer concrete legal labels used in the Act.

EXAMPLES (input → output)
- "What do I need to study abroad?" → student visa
- "How do I appeal a decision?" → judicial review
- "My tourist visa expired — what now?" → visa overstay
- "Will a criminal conviction stop my visa?" → character requirements

FAILSAFE
- If the question is too vague, pick the most likely specific legal concept rather than returning a multi-concept or generic phrase. Return exactly ONE term.

Return only the single search term now."""
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
    
    def embed_search_term(self, search_term: str):
        """Embed a search term using the sentence transformer model"""
        # if self.embedding_model is None:
        #     self.initialize_embedding_model()
        
        start_embed = time.time()
        embedding = get_embedding(search_term)
        end_embed = time.time()
        print(f"Embedding took {end_embed - start_embed:.8f} seconds")
        return embedding