import os
import requests
import zipfile
import shutil
from tqdm import tqdm

def download_file(url, filename):
    """Download file from URL with progress bar"""
    print(f"Downloading {filename}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Get file size for progress bar
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file:
        if total_size == 0:
            file.write(response.content)
        else:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        pbar.update(len(chunk))
    
    print(f"✅ Downloaded {filename} successfully!")

def extract_zip(zip_path, extract_to):
    """Extract ZIP file to specified directory"""
    print(f"Extracting {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    print(f"✅ Extracted to {extract_to} successfully!")

def setup_vector_database():
    """Main function to download and setup vector database"""
    
    # Configuration
    GDRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id=1e53smjKEAGRn36hcaWKUWjSPci4-ZgLa"
    ZIP_FILENAME = "vector_database.zip"
    EXTRACT_DIR = "."  # Current directory
    VECTOR_DB_DIR = "vector_database"
    
    try:
        # Check if vector database already exists
        if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
            print(f"✅ Vector database already exists at {VECTOR_DB_DIR}")
            return True
        
        print("🚀 Setting up vector database...")
        
        # Step 1: Download the ZIP file
        download_file(GDRIVE_DOWNLOAD_URL, ZIP_FILENAME)
        
        # Step 2: Extract the ZIP file
        extract_zip(ZIP_FILENAME, EXTRACT_DIR)
        
        # Step 3: Clean up ZIP file
        os.remove(ZIP_FILENAME)
        print(f"🗑️  Cleaned up {ZIP_FILENAME}")
        
        # Step 4: Verify extraction
        if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
            print(f"✅ Vector database setup complete!")
            print(f"📁 Database location: {os.path.abspath(VECTOR_DB_DIR)}")
            
            # List contents for verification
            db_contents = os.listdir(VECTOR_DB_DIR)
            print(f"📋 Database contents: {db_contents}")
            
            return True
        else:
            print("❌ Vector database setup failed - directory is empty or missing")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up vector database: {str(e)}")
        
        # Clean up on error
        if os.path.exists(ZIP_FILENAME):
            os.remove(ZIP_FILENAME)
            
        return False

if __name__ == "__main__":
    success = setup_vector_database()
    if success:
        print("🎉 Vector database is ready to use!")
    else:
        print("💥 Vector database setup failed!")