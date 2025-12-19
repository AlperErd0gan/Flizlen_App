
import os
import json
import pickle
import numpy as np
import google.generativeai as genai
from typing import List, Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import database, handling potential path issues
try:
    from backend import database
except ImportError:
    import database

class LightweightRAG:
    def __init__(self):
        self.documents = []  # Stores metadata and text
        self.embeddings = None # Stores numpy array of embeddings
        # GeminiClient handles API keys and configuration
        from backend.gemini_client import gemini_client
        self.client = gemini_client
        
        self.embedding_model = "models/text-embedding-004" 
        self.cache_file = os.path.join(os.path.dirname(__file__), "rag_cache.pkl")

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text"""
        try:
            # text-embedding-004 supports 768 dimensions
            # Use GeminiClient for retry logic
            result = self.client.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            return np.array(result['embedding'])
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return np.zeros(768) # Return zero vector on failure

    def load_data(self, force_refresh: bool = False):
        """Load data from SQLite and build index"""
        # 1. Try to load from cache first
        if not force_refresh and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.embeddings = data['embeddings']
                logger.info(f"Loaded {len(self.documents)} documents from cache.")
                return
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")

        # 2. Fetch from Database
        logger.info("Fetching fresh data from database...")
        all_docs = []
        
        # Fetch News
        try:
            news_items = database.get_all_news()
            for item in news_items:
                text = f"News Title: {item['title']}\nSummary: {item['summary']}\nContent: {item['content']}"
                all_docs.append({
                    "id": f"news_{item['id']}",
                    "type": "news",
                    "content": text,
                    "metadata": item
                })
        except Exception as e:
            logger.error(f"Error fetching news: {e}")

        # Fetch Tips
        try:
            tips_items = database.get_all_tips()
            for item in tips_items:
                text = f"Tip Title: {item['title']}\nDifficulty: {item.get('difficulty', 'General')}\nContent: {item['content']}"
                all_docs.append({
                    "id": f"tip_{item['id']}",
                    "type": "tip",
                    "content": text,
                    "metadata": item
                })
        except Exception as e:
            logger.error(f"Error fetching tips: {e}")

        if not all_docs:
            logger.warning("No documents found in database.")
            return

        # 3. Create Embeddings (Batching if possible, but loop for safety)
        # Note: Gemini API has rate limits. simple loop is fine for small DB.
        embeddings_list = []
        logger.info(f"Embedding {len(all_docs)} documents...")
        
        batch_texts = [d['content'] for d in all_docs]
        
        # Batch processing (Gemini accepts batches)
        # Check API limits, usually 100 per call is safe for text-embedding-004
        BATCH_SIZE = 20 
        for i in range(0, len(batch_texts), BATCH_SIZE):
            batch = batch_texts[i:i+BATCH_SIZE]
            try:
                # Proper batch embedding call
                result = self.client.embed_content(
                    model=self.embedding_model,
                    content=batch,
                    task_type="retrieval_document"
                )
                # Helper: embed_content returns dict, if batch it returns 'embedding' as list of lists
                # BUT the python library behavior varies slightly by version. 
                # Ideally 'embedding' key contains the list.
                if 'embedding' in result:
                    batch_embeddings = result['embedding']
                    embeddings_list.extend(batch_embeddings)
                else:
                    # Fallback if structure is different
                    logger.error("Unexpected embedding result format")
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}. Falling back to single.")
                # Fallback to single
                for text in batch:
                    embeddings_list.append(self._get_embedding(text))

        # 4. Finalize
        self.documents = all_docs
        # Ensure we have consistent shapes
        if len(embeddings_list) != len(all_docs):
            logger.error("Mismatch in docs and embeddings counts!")
            # Fallback re-construct to be safe
            self.embeddings = np.array([np.zeros(768)])
        else:
            self.embeddings = np.array(embeddings_list)

        # 5. Save Cache
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'embeddings': self.embeddings
                }, f)
        except Exception as e:
            logger.error(f"Could not save cache: {e}")
            
        logger.info("RAG Index build completed.")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant documents"""
        if self.embeddings is None or len(self.documents) == 0:
            return []

        try:
            # Embed query
            query_content = self.client.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"
            )
            query_vec = np.array(query_content['embedding'])
            
            # Simple Cosine Similarity: (A . B) / (|A| * |B|)
            # Assuming vectors might not be normalized from API
            
            # Normalize embeddings (if not already)
            norm_docs = np.linalg.norm(self.embeddings, axis=1)
            norm_query = np.linalg.norm(query_vec)
            
            if norm_query == 0:
                return []
                
            # Avoid division by zero
            norm_docs[norm_docs == 0] = 1e-10
            
            # Dot Product
            dot_products = np.dot(self.embeddings, query_vec)
            
            # Cosine Similarity
            similarities = dot_products / (norm_docs * norm_query)
            
            # Get top K indices
            # argsort sorts ascending, so we take last k and reverse
            top_k_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_k_indices:
                score = similarities[idx]
                if score < 0.35: # Threshold for relevance
                    continue
                
                doc = self.documents[idx].copy()
                doc['score'] = float(score)
                results.append(doc)
                
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

# Singleton instance
rag_system = LightweightRAG()
