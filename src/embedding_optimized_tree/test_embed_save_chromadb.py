

# --- Imports
from sentence_transformers import SentenceTransformer
import torch, os
from chromadb import PersistentClient
from chromadb.config import Settings

# --- Setup
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

texts = [
    "Artificial intelligence is transforming industries.",
    "Python is a popular programming language.",
    "Space exploration is the future of humanity.",
    "Data science is a blend of statistics and programming."
]
embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)

# --- PersistentClient writes to disk on each add
persist_dir = "vector_database"
client = PersistentClient(
    path=persist_dir,
    settings=Settings(anonymized_telemetry=False)
)

coll = client.get_or_create_collection("my_collection")
coll.add(
    embeddings=embeddings.tolist(),
    documents=texts,
    ids=[f"doc_{i}" for i in range(len(texts))]
)
print(f"✅ Data added. Should be on-disk under: {os.path.abspath(persist_dir)}")

# --- Query
query = "What is AI?"
q_emb = model.encode([query], convert_to_numpy=True)
res = coll.query(query_embeddings=q_emb.tolist(), n_results=2)
print("🔍 Results:", res)

# --- List what got written
print("On-disk files:", os.listdir(persist_dir))
