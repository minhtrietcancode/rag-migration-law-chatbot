from sentence_transformers import SentenceTransformer
import numpy as np

# Example header string
headers = ["Arrival, presence and departure of persons",
           "Preliminary",
           "Migration agents and immigration assistance",
           "Offences relating to decisions under Act",
           "Civil penalties"]

# Load a pre-trained sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate the embedding (vector) for headers
header_vectors = [model.encode(header) for header in headers]

sample_keyword = "violate the rules"
# Embed the sample keyword
keyword_vector = model.encode(sample_keyword)

# Calculate and print similarity scores (cosine similarity)
for header, header_vector in zip(headers, header_vectors):
    similarity = abs(np.dot(header_vector, keyword_vector) / (np.linalg.norm(header_vector) * np.linalg.norm(keyword_vector)))
    print(f"Similarity between '{sample_keyword}' and '{header}': {similarity:.4f}")