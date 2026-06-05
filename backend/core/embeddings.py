from sentence_transformers import SentenceTransformer
from typing import List

# We use all-MiniLM-L6-v2 because it's extremely fast, runs locally for free, 
# and produces high-quality 384-dimensional embeddings perfect for our RAG use case.
MODEL_NAME = 'all-MiniLM-L6-v2'

# Initialize the model once when the module loads
# This will download the model weights (approx 80MB) on first run
try:
    embedder = SentenceTransformer(MODEL_NAME)
except Exception as e:
    print(f"Failed to load sentence transformer model: {e}")
    embedder = None

def get_embedding(text: str) -> List[float]:
    """
    Generates a 384-dimensional vector embedding for a given text string.
    """
    if not embedder:
        raise RuntimeError("Embedding model is not loaded.")
        
    # Clean up text by removing excessive whitespace
    clean_text = " ".join(text.split())
    
    # Generate embedding and convert to list of floats for pgvector
    embedding = embedder.encode(clean_text)
    return embedding.tolist()

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a batch of text strings efficiently.
    """
    if not embedder:
        raise RuntimeError("Embedding model is not loaded.")
        
    clean_texts = [" ".join(text.split()) for text in texts]
    embeddings = embedder.encode(clean_texts)
    return embeddings.tolist()
