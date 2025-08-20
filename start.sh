#!/bin/bash
# Initialize vector database
mkdir -p vector_database
python data_preparation/embedding_optimized_tree/embed_save_chromadb.py
# Start the Flask app
python src/app.py