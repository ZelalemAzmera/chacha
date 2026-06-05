from typing import List, Dict, Any
from core.embeddings import get_embeddings, get_embedding
from db.supabase import get_supabase_client

supabase = get_supabase_client()

def store_document_chunks(agent_id: str, material_id: str, chunks: List[str]) -> bool:
    """
    Embeds text chunks and stores them in Supabase pgvector.
    """
    if not chunks:
        return False
        
    try:
        # Generate embeddings for all chunks in a single batch
        embeddings = get_embeddings(chunks)
        
        # Prepare data for insertion
        records = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            records.append({
                "agent_id": agent_id,
                "material_id": material_id,
                "content": chunk,
                "embedding": embedding,
                "metadata": {"chunk_index": i}
            })
            
        # Insert into Supabase
        # Note: Depending on batch size, you might want to paginate this
        supabase.table("chunks").insert(records).execute()
        return True
    except Exception as e:
        print(f"Error storing chunks in pgvector: {e}")
        return False

def retrieve_context(agent_id: str, query_text: str, top_k: int = 5) -> str:
    """
    Embeds the user's query and searches the agent's knowledge base using pgvector.
    Returns the concatenated context string.
    """
    try:
        query_embedding = get_embedding(query_text)
        
        # Call the Supabase RPC function for vector similarity search
        # Note: We need to create this RPC function in Supabase SQL Editor
        result = supabase.rpc(
            "match_chunks",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.5, # Adjust based on needed confidence
                "match_count": top_k,
                "p_agent_id": agent_id
            }
        ).execute()
        
        if not result.data:
            return ""
            
        # Concatenate matched chunks
        contexts = [item["content"] for item in result.data]
        return "\n\n---\n\n".join(contexts)
        
    except Exception as e:
        print(f"Error retrieving context from pgvector: {e}")
        return ""
