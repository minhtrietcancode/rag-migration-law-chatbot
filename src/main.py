# main.py
from search_term_handler_package.search_term_handler import SearchTermHandler
from database_admin_package.database_admin import DatabaseAdmin
from my_searcher_package.my_searcher import MySearcher
from my_metadata_loader_package.my_metadata_loader import MyMetadataLoader
import time

class MigrationActPipeline:
    """Main pipeline for processing Migration Act questions"""
    
    def __init__(self):
        print("🚀 Initializing Migration Act Search Pipeline...")
        
        # Initialize all components
        self.search_term_handler = SearchTermHandler()
        self.database_admin = DatabaseAdmin()
        self.searcher = MySearcher()
        self.metadata_loader = MyMetadataLoader()
        
        # Pre-load all data (do this once at startup)
        self._initialize_all_components()
    
    def _initialize_all_components(self):
        """Pre-initialize all components to avoid reloading during queries"""
        print("\n📋 Pre-loading all components...")
        
        # Initialize embedding model
        print("1. Loading embedding model...")
        self.search_term_handler.initialize_embedding_model()
        
        # Initialize ChromaDB
        print("2. Loading ChromaDB collection...")
        collection = self.database_admin.initialize_chromadb()
        if collection is None:
            raise Exception("Failed to initialize ChromaDB")
        
        # Load search tree
        print("3. Loading search tree...")
        tree = self.searcher.load_search_tree()
        if tree is None:
            raise Exception("Failed to load search tree")
        
        # Load hashmap
        print("4. Loading metadata hashmap...")
        hashmap = self.metadata_loader.load_hashmap()
        if hashmap is None:
            raise Exception("Failed to load hashmap")
        
        print("✅ All components initialized successfully!\n")
    
    def process_question(self, user_question: str, limit: int = 3):
        """
        Process a single user question through the full pipeline
        
        Args:
            user_question: User's question about Migration Act
            limit: Maximum number of sections to return
        
        Returns:
            dict: Results containing search term, sections found, and content
        """
        print(f"🔄 Processing question: '{user_question}'")
        print("=" * 80)
        
        results = {
            'question': user_question,
            'search_term': None,
            'sections_found': [],
            'content': []
        }
        
        try:
            # Step 1: Generate search term
            print("Step 1: Generating search term...")
            search_term = self.search_term_handler.generate_search_term(user_question)
            if not search_term:
                print("❌ Failed to generate search term")
                return results
            
            results['search_term'] = search_term
            
            # Step 2: Embed the search term
            print("Step 2: Embedding search term...")
            search_term_vector = self.search_term_handler.embed_search_term(search_term)
            
            # Step 3: Search for relevant sections
            print("Step 3: Searching for relevant sections...")
            sections = self.searcher.search_term_on_tree(
                search_term_vector=search_term_vector,
                database_admin=self.database_admin,
                limit=limit
            )
            
            if not sections:
                print("❌ No relevant sections found")
                return results
            
            results['sections_found'] = sections
            print(f"✅ Found {len(sections)} relevant sections")
            
            # Step 4: Get content for each section
            print("Step 4: Retrieving content for sections...")
            for i, section in enumerate(sections, 1):
                print(f"  📄 Getting content for section {i}: {section}")
                try:
                    content = self.metadata_loader.get_section_content(section)
                    if content:
                        results['content'].append({
                            'section_name': section,
                            'content': content
                        })
                        print(f"    ✅ Retrieved {len(content)} characters")
                    else:
                        print(f"    ⚠️ No content found for section: {section}")
                except Exception as e:
                    print(f"    ❌ Error retrieving content for {section}: {str(e)}")
            
            print(f"✅ Successfully processed question. Found content for {len(results['content'])} sections.")
            
        except Exception as e:
            print(f"❌ Error processing question: {str(e)}")
        
        return results
    
    def display_results(self, results):
        """Display results in a formatted way"""
        print("\n" + "=" * 100)
        print("🎯 SEARCH RESULTS")
        print("=" * 100)
        
        print(f"❓ Question: {results['question']}")
        print(f"🔍 Search Term: {results['search_term']}")
        print(f"📊 Sections Found: {len(results['sections_found'])}")
        
        if results['content']:
            print(f"📄 Content Retrieved: {len(results['content'])} sections")
            print("\n" + "-" * 50)
            
            for i, section_data in enumerate(results['content'], 1):
                print(f"\n🔸 SECTION {i}: {section_data['section_name']}")
                print("-" * 50)
                # Show first 500 characters of content
                content_preview = section_data['content'][:500]
                print(content_preview)
                if len(section_data['content']) > 500:
                    print(f"... [Content truncated - Total: {len(section_data['content'])} characters]")
                print("-" * 50)
        else:
            print("❌ No content retrieved")
        
        print("\n" + "=" * 100 + "\n")

def main():
    """Main function to run the pipeline with sample questions"""
    
    # Sample questions for testing
    sample_questions = [
        "What happens if I overstay my tourist visa in Australia?",
        "How do I appeal a visa decision that was rejected?"
    ]
    
    try:
        # Initialize the pipeline (this does all the heavy loading once)
        pipeline = MigrationActPipeline()
        
        # Process each sample question
        for i, question in enumerate(sample_questions, 1):
            print(f"\n🔥 PROCESSING SAMPLE QUESTION {i}/{len(sample_questions)}")
            print("=" * 120)
            
            # Process the question
            start_time = time.time()
            results = pipeline.process_question(question, limit=3)
            end_time = time.time()
            
            # Display results
            pipeline.display_results(results)
            
            print(f"⏱️ Total processing time: {end_time - start_time:.2f} seconds")
            
            # Add separator between questions
            if i < len(sample_questions):
                print("\n" + "🔄" * 50 + " NEXT QUESTION " + "🔄" * 50)
        
        print("\n🎉 All sample questions processed successfully!")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")

if __name__ == "__main__":
    main()