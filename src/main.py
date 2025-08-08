# main.py
from search_term_handler_package.search_term_handler import SearchTermHandler
from database_admin_package.database_admin import DatabaseAdmin
from my_searcher_package.my_searcher import MySearcher
from my_metadata_loader_package.my_metadata_loader import MyMetadataLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import time
import config

class MigrationActChatbot:
    """Intelligent chatbot that can search Migration Act when needed"""
    
    def __init__(self):
        print("🤖 Initializing Migration Act Chatbot...")
        
        # Initialize search pipeline components
        self.search_term_handler = SearchTermHandler()
        self.database_admin = DatabaseAdmin()
        self.searcher = MySearcher()
        self.metadata_loader = MyMetadataLoader()
        
        # Initialize LLM for chat
        self.chat_llm = None
        self.decision_chain = None
        self.response_chain = None
        
        # Pre-load all components
        self._initialize_all_components()
        self._initialize_chat_llm()
        
        print("🎉 Chatbot ready! Type 'quit' or 'exit' to end the conversation.\n")
    
    def _initialize_all_components(self):
        """Pre-initialize search components"""
        print("\n📋 Loading search components...")
        
        print("1. Loading embedding model...")
        self.search_term_handler.initialize_embedding_model()
        
        print("2. Loading ChromaDB collection...")
        collection = self.database_admin.initialize_chromadb()
        if collection is None:
            raise Exception("Failed to initialize ChromaDB")
        
        print("3. Loading search tree...")
        tree = self.searcher.load_search_tree()
        if tree is None:
            raise Exception("Failed to load search tree")
        
        print("4. Loading metadata hashmap...")
        hashmap = self.metadata_loader.load_hashmap()
        if hashmap is None:
            raise Exception("Failed to load hashmap")
    
    def _initialize_chat_llm(self):
        """Initialize LLM for chat and decision making"""
        print("5. Initializing chat LLM...")
        
        self.chat_llm = ChatOpenAI(
            openai_api_key=config.OPENROUTER_API_KEY,
            openai_api_base=config.OPENROUTER_API_BASE,
            model=config.MODEL_NAME,
            temperature=0.3,
            max_tokens=500
        )
        
        # Decision prompt - determines if search is needed
        decision_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Migration Act assistant. Your job is to determine if a user's question requires searching the Migration Act database.

RESPOND WITH EXACTLY ONE WORD: "SEARCH" or "CHAT"

Use "SEARCH" if the question is about:
- Specific visa requirements, processes, or rules
- Legal obligations or penalties in Australian migration law
- Specific sections or provisions of the Migration Act
- Immigration procedures, applications, or decisions
- Migration agent regulations
- Court proceedings related to migration
- Any detailed legal information about Australian immigration

Use "CHAT" if the question is:
- General greetings or pleasantries
- Questions about how this chatbot works
- Non-migration related topics
- Very basic questions you can answer from general knowledge
- Personal opinions or advice not requiring specific legal text

Examples:
"Hello, how are you?" → CHAT
"What visa do I need to work in Australia?" → SEARCH
"How does this chatbot work?" → CHAT
"What happens if I overstay my visa?" → SEARCH
"What's the weather like?" → CHAT
"Can I appeal a visa rejection?" → SEARCH

Remember: RESPOND WITH ONLY ONE WORD: "SEARCH" or "CHAT"""
            ),
            ("user", "{question}")
        ])
        
        # Response prompt - generates final response
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful Migration Act assistant. Generate a natural, conversational response based on the context provided.

IMPORTANT RULES:
1. If search_results contain relevant information, use it to provide a detailed, helpful answer
2. If search_results are empty or irrelevant, politely say you don't have specific information about that topic in the Migration Act
3. Always be helpful and professional
4. Don't make up legal information - only use what's provided in search_results
5. If the question doesn't require search, provide a friendly general response
6. Keep responses conversational and user-friendly, not robotic

When using search results:
- Cite relevant section numbers when available
- Explain legal concepts in plain English
- Be specific about what the Act says

When search results are not helpful:
- Say something like "I don't have specific information about that in the Migration Act" 
- Suggest they consult official sources or migration professionals
- Don't apologize excessively"""),
            ("user", """
User Question: {question}

Search Results: {search_results}

Generate a helpful response:""")
        ])
        
        self.decision_chain = decision_prompt | self.chat_llm
        self.response_chain = response_prompt | self.chat_llm
        
        print("✅ Chat LLM initialized successfully!")
    
    def _should_search(self, user_question: str) -> bool:
        """Determine if the question requires searching Migration Act"""
        try:
            start_time = time.time()
            response = self.decision_chain.invoke({"question": user_question})
            decision = response.content.strip().upper()
            end_time = time.time()
            
            print(f"🧠 Decision: {decision} ({end_time - start_time:.2f}s)")
            return decision == "SEARCH"
        except Exception as e:
            print(f"❌ Decision error: {e}")
            # Default to search if unsure
            return True
    
    def _search_migration_act(self, user_question: str) -> str:
        """Search Migration Act and return formatted results"""
        print("🔍 Searching Migration Act database...")
        
        try:
            # Generate search term
            search_term = self.search_term_handler.generate_search_term(user_question)
            if not search_term:
                return "No search results - could not generate search term."
            
            print(f"📝 Search term: '{search_term}'")
            
            # Embed and search
            search_term_vector = self.search_term_handler.embed_search_term(search_term)
            sections = self.searcher.search_term_on_tree(
                search_term_vector=search_term_vector,
                database_admin=self.database_admin,
                limit=3
            )
            
            if not sections:
                return "No relevant sections found in Migration Act."
            
            # Get content for sections
            search_results = f"Search term used: {search_term}\n\n"
            search_results += f"Found {len(sections)} relevant sections:\n\n"
            
            for i, section in enumerate(sections, 1):
                try:
                    content = self.metadata_loader.get_section_content(section)
                    if content:
                        # Extract section number and clean content
                        section_parts = section.split('_')
                        section_number = section_parts[1] if len(section_parts) > 1 else "Unknown"
                        
                        search_results += f"SECTION {i} (Section {section_number}):\n"
                        search_results += content[:2000] + "\n\n"  # Limit content length
                except Exception as e:
                    print(f"Error getting content for {section}: {e}")
                    continue
            
            return search_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return f"Search error: {str(e)}"
    
    def _generate_response(self, user_question: str, search_results: str = "") -> str:
        """Generate final response using LLM"""
        try:
            start_time = time.time()
            response = self.response_chain.invoke({
                "question": user_question,
                "search_results": search_results
            })
            end_time = time.time()
            
            print(f"💬 Response generated ({end_time - start_time:.2f}s)")
            return response.content.strip()
        except Exception as e:
            print(f"❌ Response generation error: {e}")
            return "I apologize, I'm having trouble generating a response right now."
    
    def process_user_message(self, user_message: str) -> str:
        """Process a single user message and return response"""
        print(f"\n{'='*60}")
        print(f"User: {user_message}")
        print(f"{'='*60}")
        
        # Step 1: Decide if search is needed
        needs_search = self._should_search(user_message)
        
        if needs_search:
            print("📊 Analysis: Migration Act search required")
            # Step 2: Search Migration Act
            search_results = self._search_migration_act(user_message)
            
            # Step 3: Generate response with search results
            response = self._generate_response(user_message, search_results)
        else:
            print("💭 Analysis: General chat response")
            # Generate response without search
            response = self._generate_response(user_message, "")
        
        return response
    
    def start_chat(self):
        """Start the interactive chat loop"""
        print("🤖 Migration Act Chatbot")
        print("Ask me anything about Australian Migration Act!")
        print("Type 'quit', 'exit', or 'bye' to end the conversation.\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thank you for using Migration Act Chatbot! Goodbye!")
                    break
                
                if not user_input:
                    print("Please enter a question or type 'quit' to exit.\n")
                    continue
                
                # Process message and get response
                start_time = time.time()
                response = self.process_user_message(user_input)
                total_time = time.time() - start_time
                
                # Display response
                print(f"\n🤖 Bot: {response}")
                print(f"\n⏱️ Total response time: {total_time:.2f} seconds")
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Please try again or type 'quit' to exit.\n")

def main():
    """Main function to start the chatbot"""
    try:
        chatbot = MigrationActChatbot()
        chatbot.start_chat()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")

if __name__ == "__main__":
    main()