#!/usr/bin/env python3
"""
Memory Usage Profiler for RAG Migration Law Chatbot
This script helps identify memory bottlenecks during application startup and runtime.
"""

import os
import sys
import gc
import json
import time
import psutil
from datetime import datetime

class MemoryProfiler:
    """
    A utility class to monitor memory usage throughout application lifecycle
    """
    
    def __init__(self, log_file=None):
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = self.get_current_memory()
        self.log_file = log_file
        self.measurements = []
        
        print("="*60)
        print(f"Memory Profiler Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Initial Memory Usage: {self.baseline_memory:.1f} MB")
        print("="*60)
    
    def get_current_memory(self):
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def print_memory_usage(self, stage, details=None):
        """Print memory usage for a specific stage"""
        current_memory = self.get_current_memory()
        delta = current_memory - self.baseline_memory
        
        # Store measurement
        measurement = {
            'stage': stage,
            'memory_mb': current_memory,
            'delta_mb': delta,
            'timestamp': datetime.now(),
            'details': details
        }
        self.measurements.append(measurement)
        
        # Print to console
        print(f"{stage}: {current_memory:.1f} MB (+{delta:.1f} MB)")
        if details:
            print(f"   └─ Details: {details}")
        
        # Log to file if specified
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"{measurement['timestamp']}: {stage} - {current_memory:.1f} MB (+{delta:.1f} MB)\n")
                if details:
                    f.write(f"   Details: {details}\n")
    
    def force_cleanup(self, stage_name="Manual Cleanup"):
        """Force garbage collection and print memory after cleanup"""
        gc.collect()
        time.sleep(0.1)  # Small delay to let cleanup complete
        self.print_memory_usage(f"{stage_name} (after gc.collect())")
    
    def get_memory_summary(self):
        """Get a summary of memory usage throughout the profiling session"""
        if not self.measurements:
            return "No measurements taken"
        
        max_memory = max(self.measurements, key=lambda x: x['memory_mb'])
        total_increase = self.get_current_memory() - self.baseline_memory
        
        summary = f"""
Memory Profiling Summary:
========================
Baseline Memory: {self.baseline_memory:.1f} MB
Current Memory:  {self.get_current_memory():.1f} MB
Total Increase:  +{total_increase:.1f} MB
Peak Memory:     {max_memory['memory_mb']:.1f} MB (at {max_memory['stage']})
Measurements:    {len(self.measurements)} stages tracked
"""
        return summary

def profile_imports():
    """Profile memory usage during imports"""
    profiler = MemoryProfiler(log_file="memory_profile.log")
    
    try:
        # Stage 1: Basic Python imports
        profiler.print_memory_usage("1. Python startup (baseline)")
        
        # Stage 2: Standard library imports
        import json
        import os
        import gc
        profiler.print_memory_usage("2. Standard library imports", "json, os, gc")
        
        # Stage 3: Flask
        try:
            from flask import Flask, request, jsonify
            profiler.print_memory_usage("3. Flask imports", "Flask, request, jsonify")
        except ImportError as e:
            profiler.print_memory_usage("3. Flask imports FAILED", str(e))
        
        # Stage 4: Requests
        try:
            import requests
            profiler.print_memory_usage("4. Requests import", "requests library")
        except ImportError as e:
            profiler.print_memory_usage("4. Requests import FAILED", str(e))
        
        # Stage 5: NumPy
        try:
            import numpy as np
            profiler.print_memory_usage("5. NumPy import", "numpy library")
        except ImportError as e:
            profiler.print_memory_usage("5. NumPy import FAILED", str(e))
        
        # Stage 6: Sentence Transformers
        try:
            from sentence_transformers import SentenceTransformer
            profiler.print_memory_usage("6. SentenceTransformers import", "sentence-transformers library")
        except ImportError as e:
            profiler.print_memory_usage("6. SentenceTransformers import FAILED", str(e))
        
        # Stage 7: LangChain
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage
            profiler.print_memory_usage("7. LangChain imports", "langchain_openai, schema")
        except ImportError as e:
            profiler.print_memory_usage("7. LangChain imports FAILED", str(e))
        
        # Stage 8: ChromaDB
        try:
            import chromadb
            profiler.print_memory_usage("8. ChromaDB import", "chromadb library")
        except ImportError as e:
            profiler.print_memory_usage("8. ChromaDB import FAILED", str(e))
        
        # Stage 9: Load Sentence Transformer Model
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            profiler.print_memory_usage("9. Load SentenceTransformer model", "all-MiniLM-L6-v2")
            del model  # Clean up model
            profiler.force_cleanup("9a. After model cleanup")
        except Exception as e:
            profiler.print_memory_usage("9. Load SentenceTransformer model FAILED", str(e))
        
        # Stage 10: ChromaDB Client (if database exists)
        try:
            if os.path.exists("vector_database"):
                client = chromadb.PersistentClient(path="./vector_database")
                profiler.print_memory_usage("10. ChromaDB client connection", "PersistentClient to ./vector_database")
                del client
                profiler.force_cleanup("10a. After ChromaDB cleanup")
            else:
                profiler.print_memory_usage("10. ChromaDB client SKIPPED", "vector_database folder not found")
        except Exception as e:
            profiler.print_memory_usage("10. ChromaDB client FAILED", str(e))
        
        # Stage 11: Load JSON files (if they exist)
        json_files = [
            "final_json_searching_material/final_hashmap.json",
            "final_json_searching_material/final_search_tree_embed_id.json",
        ]
        
        for i, json_file in enumerate(json_files, 11):
            try:
                if os.path.exists(json_file):
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    file_size_mb = os.path.getsize(json_file) / 1024 / 1024
                    profiler.print_memory_usage(f"{i}. Load {os.path.basename(json_file)}", 
                                              f"File size: {file_size_mb:.1f} MB")
                    del data
                    profiler.force_cleanup(f"{i}a. After {os.path.basename(json_file)} cleanup")
                else:
                    profiler.print_memory_usage(f"{i}. Load {os.path.basename(json_file)} SKIPPED", "File not found")
            except Exception as e:
                profiler.print_memory_usage(f"{i}. Load {os.path.basename(json_file)} FAILED", str(e))
        
        # Final cleanup and summary
        profiler.force_cleanup("Final cleanup")
        
        print("\n" + profiler.get_memory_summary())
        
        # Check if we're over Render's limit
        current_memory = profiler.get_current_memory()
        if current_memory > 400:
            print(f"\n⚠️  WARNING: Memory usage ({current_memory:.1f} MB) is close to Render's 512MB limit!")
        elif current_memory > 512:
            print(f"\n❌ CRITICAL: Memory usage ({current_memory:.1f} MB) exceeds Render's 512MB limit!")
        else:
            print(f"\n✅ Memory usage ({current_memory:.1f} MB) is within Render's 512MB limit")
            
    except KeyboardInterrupt:
        print("\nProfiling interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error during profiling: {e}")
        import traceback
        traceback.print_exc()

def profile_your_app():
    """Profile your specific app components"""
    profiler = MemoryProfiler(log_file="app_memory_profile.log")
    
    try:
        # Add your specific imports and components here
        profiler.print_memory_usage("App Start")
        
        # Example: Import your custom packages
        # try:
        #     from src.database_admin_package import DatabaseAdmin
        #     profiler.print_memory_usage("DatabaseAdmin import")
        # except ImportError as e:
        #     profiler.print_memory_usage("DatabaseAdmin import FAILED", str(e))
        
        # try:
        #     from src.my_searcher_package import MySearcher
        #     profiler.print_memory_usage("MySearcher import")
        # except ImportError as e:
        #     profiler.print_memory_usage("MySearcher import FAILED", str(e))
        
        # Add more of your specific components...
        
        print(profiler.get_memory_summary())
        
    except Exception as e:
        print(f"Error profiling your app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("RAG Migration Law Chatbot - Memory Profiler")
    print("This script will help identify memory bottlenecks in your application.\n")
    
    # Check system memory
    system_memory = psutil.virtual_memory()
    print(f"System Total Memory: {system_memory.total / 1024 / 1024 / 1024:.1f} GB")
    print(f"System Available Memory: {system_memory.available / 1024 / 1024:.1f} MB")
    print(f"Render Free Tier Limit: 512 MB")
    print("-" * 60)
    
    # Run the import profiling
    profile_imports()
    
    print("\n" + "="*60)
    print("Profiling completed! Check 'memory_profile.log' for detailed logs.")
    print("="*60)