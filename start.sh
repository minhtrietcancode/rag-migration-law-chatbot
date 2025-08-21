#!/bin/bash

echo "🚀 Starting Migration Act Assistant deployment..."

# Step 1: Setup vector database
echo "📁 Setting up vector database..."
python download_vector_db.py

# Check if vector database setup was successful
if [ $? -eq 0 ]; then
    echo "✅ Vector database ready!"
else
    echo "❌ Vector database setup failed!"
    exit 1
fi

# Step 2: Start Flask application
echo "🌐 Starting Flask application..."
gunicorn --bind 0.0.0.0:${PORT:-5000} app:app