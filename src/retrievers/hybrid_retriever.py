"""
Hybrid Retrieval System combining dense vectors (semantic) and sparse (BM25)
"""

from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class HybridRetriever:
    """Combines semantic search with keyword search"""

    def __init__(self, documents: List[Dict], dense_weight=0.7, sparse_weight=0.3):
        self.documents = documents
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Prepare dense embeddings
        self.doc_embeddings = self._embed_documents()

        # Prepare BM25
        tokenized_docs = [doc['content'].lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def _embed_documents(self):
        """Create embeddings for all documents"""
        texts = [doc['content'] for doc in self.documents]
        return self.embedding_model.encode(texts, show_progress_bar=True)

    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        """Hybrid retrieval with RRF fusion"""

        # Dense retrieval
        query_embedding = self.embedding_model.encode([query])[0]
        dense_scores = cosine_similarity([query_embedding], self.doc_embeddings)[0]

        # Sparse retrieval
        tokenized_query = query.lower().split()
        sparse_scores = self.bm25.get_scores(tokenized_query)

        # Normalize scores
        dense_scores = (dense_scores - dense_scores.min()) / (dense_scores.max() - dense_scores.min() + 1e-10)
        sparse_scores = (sparse_scores - sparse_scores.min()) / (sparse_scores.max() - sparse_scores.min() + 1e-10)

        # Combine scores
        combined_scores = (self.dense_weight * dense_scores +
                          self.sparse_weight * sparse_scores)

        # Get top-k
        top_indices = np.argsort(combined_scores)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            doc = self.documents[idx].copy()
            doc['score'] = float(combined_scores[idx])
            doc['dense_score'] = float(dense_scores[idx])
            doc['sparse_score'] = float(sparse_scores[idx])
            results.append(doc)

        return results
