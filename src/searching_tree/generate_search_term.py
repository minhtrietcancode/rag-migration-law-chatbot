import os
import re
from typing import Optional, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

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

def batch_generate_search_terms(questions: List[str]) -> List[tuple]:
    """
    Generate search terms for multiple questions.
    
    Returns:
        List of tuples: (question, search_term)
    """
    results = []
    for question in questions:
        search_term = generate_search_term_from_question(question)
        results.append((question, search_term))
    return results

# --- Enhanced testing and validation
if __name__ == "__main__":
    test_questions = [
        "What happens if someone overstays their tourist visa in Australia?",
        # "How do I apply for a bridging visa while my main application is being processed?",
        # "What's the process for visa cancellation and can it be appealed?",
        # "Are there any special visas for people who work on ships or maritime industry?",
        # "What do I need to study in Australia?",
        # "Can I work while on a tourist visa?",
        # "How to bring my family to Australia?",
        # "What if my visa application gets rejected?",
        # "Can criminals get Australian visas?",
        # "What are the health requirements for migration to Australia?",
    ]
    
    print("🧪 TESTING OPTIMIZED SEARCH TERM GENERATION")
    print("="*80)
    
    results = batch_generate_search_terms(test_questions)
    
    success_count = 0
    for i, (question, search_term) in enumerate(results, 1):
        print(f"\n{i}. Question: {question}")
        if search_term:
            print(f"   ✅ Search term: '{search_term}'")
            success_count += 1
        else:
            print("   ❌ Failed to generate search term")
    
    print(f"\n" + "="*80)
    print(f"📊 Success rate: {success_count}/{len(test_questions)} ({success_count/len(test_questions)*100:.1f}%)")
    
    # Test edge cases
    print("\n🧪 TESTING EDGE CASES")
    print("-"*40)
    
    edge_cases = [
        "",  # Empty string
        "   ",  # Whitespace only
        "What?",  # Very short
        "This is not related to migration at all, just random text about cooking recipes",  # Irrelevant
    ]
    
    for case in edge_cases:
        print(f"Input: '{case}'")
        result = generate_search_term_from_question(case)
        print(f"Result: {result}\n")