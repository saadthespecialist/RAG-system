"""
ChromaDB Vector Store Integration
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
import json


class VectorStore:
    """ChromaDB-based vector store for semantic search"""

    def __init__(self, collection_name: str = "rag_products", persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client and collection"""
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Use ChromaDB's built-in sentence transformer embeddings
        # This uses a lightweight model that doesn't require PyTorch installation
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Add documents to the vector store"""
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query the vector store for similar documents"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )

        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })

        return formatted_results

    def get_count(self) -> int:
        """Get the number of documents in the collection"""
        return self.collection.count()

    def clear(self):
        """Clear all documents from the collection"""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )


class HybridVectorStore:
    """Combines ChromaDB semantic search with BM25 keyword search"""

    def __init__(self, collection_name: str = "rag_products", persist_directory: str = "./chroma_db"):
        """Initialize hybrid search with both vector and keyword search"""
        self.vector_store = VectorStore(collection_name, persist_directory)
        self.bm25 = None  # Will be set when building index
        self.documents = []
        self.metadata = []

    def build_index(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        """Build both vector and BM25 indices"""
        from rank_bm25 import BM25Okapi

        # Store documents and metadata
        self.documents = documents
        self.metadata = metadatas

        # Build vector index (ChromaDB)
        ids = [f"doc_{i}" for i in range(len(documents))]

        # Convert metadata to JSON-serializable format
        serializable_metadatas = []
        for meta in metadatas:
            # Convert metadata to string representation for ChromaDB
            serializable_meta = {}
            for key, value in meta.items():
                if isinstance(value, (dict, list)):
                    serializable_meta[key] = json.dumps(value)
                else:
                    serializable_meta[key] = str(value)
            serializable_metadatas.append(serializable_meta)

        self.vector_store.add_documents(documents, serializable_metadatas, ids)

        # Build BM25 index
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def hybrid_search(self, query: str, top_k: int = 5, alpha: float = 0.7) -> List[Dict[str, Any]]:
        """
        Hybrid search combining semantic (ChromaDB) and keyword (BM25) search

        Args:
            query: Search query
            top_k: Number of results to return
            alpha: Weight for semantic search (0-1). 1-alpha is weight for BM25.
        """
        # Get semantic search results (more results for better fusion)
        vector_results = self.vector_store.query(query, top_k=top_k * 2)

        # Get BM25 keyword search results
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Create score dictionary combining both methods
        combined_scores = {}

        # Add semantic scores (convert distances to scores, lower distance = higher score)
        for result in vector_results:
            doc_id = result['id']
            idx = int(doc_id.split('_')[1])
            # Convert distance to similarity score (1 - normalized_distance)
            # Typical cosine distances are 0-2, so normalize
            similarity_score = 1.0 - (result['distance'] / 2.0) if result['distance'] else 1.0
            combined_scores[idx] = alpha * similarity_score

        # Add BM25 scores (normalize by max score)
        max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
        for idx, score in enumerate(bm25_scores):
            normalized_score = score / max_bm25
            if idx in combined_scores:
                combined_scores[idx] += (1 - alpha) * normalized_score
            else:
                combined_scores[idx] = (1 - alpha) * normalized_score

        # Sort by combined score and get top-k
        top_indices = sorted(combined_scores.keys(), key=lambda i: combined_scores[i], reverse=True)[:top_k]

        # Format results
        results = []
        for idx in top_indices:
            if combined_scores[idx] > 0:
                # Reconstruct metadata from stored data
                metadata = self.metadata[idx]
                results.append({
                    'score': combined_scores[idx],
                    'metadata': metadata,
                    'document': self.documents[idx]
                })

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the index"""
        return {
            'vector_count': self.vector_store.get_count(),
            'bm25_count': len(self.documents),
            'total_documents': len(self.metadata)
        }
