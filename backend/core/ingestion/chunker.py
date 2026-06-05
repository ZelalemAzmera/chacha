import re
from typing import List

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Splits text into chunks of approximately `chunk_size` words with an `overlap` 
    to preserve context across chunk boundaries.
    """
    # Basic cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split(' ')
    
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        
        # Move forward, minus the overlap
        i += chunk_size - overlap
        
    return chunks
