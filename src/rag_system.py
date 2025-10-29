"""
Main RAG System orchestrating all components
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from retrievers.hybrid_retriever import HybridRetriever

class AdvancedRAGSystem:
    """Complete RAG system with all advanced features"""

    def __init__(self, data_path: str = "data/processed/representations.json"):
        self.data_path = Path(data_path)
        self.documents = self._load_documents()
        self.retriever = HybridRetriever(self.documents)

    def _load_documents(self) -> List[Dict]:
        """Load processed documents"""
        if self.data_path.exists():
            with open(self.data_path, 'r') as f:
                return json.load(f)
        return []

    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        Answer a question using RAG

        Args:
            question: User question
            top_k: Number of documents to retrieve

        Returns:
            Dictionary with answer, sources, and citations
        """
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve(question, top_k=top_k)

        # Step 2: Format context
        context = self._format_context(retrieved_docs)

        # Step 3: Generate answer (placeholder - would use LLM in production)
        answer = self._generate_answer(question, context, retrieved_docs)

        return answer

    def _format_context(self, docs: List[Dict]) -> str:
        """Format retrieved documents into context"""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"[{i}] {doc['content'][:500]}...")
        return "\n\n".join(context_parts)

    def _generate_answer(self, question: str, context: str, sources: List[Dict]) -> Dict:
        """Generate answer with citations"""
        # In production, this would call an LLM
        # For demo, return structured response

        return {
            "question": question,
            "answer": f"Based on the product catalog: {context[:200]}...",
            "sources": [
                {
                    "doc_id": doc['doc_id'],
                    "type": doc['type'],
                    "source": doc['metadata']['source'],
                    "score": doc['score'],
                    "excerpt": doc['content'][:150]
                }
                for doc in sources[:3]
            ],
            "confidence": sources[0]['score'] if sources else 0.0
        }

# Demo function
def demo():
    """Demonstrate RAG system"""
    print("Initializing Advanced RAG System...\n")

    rag = AdvancedRAGSystem()
    print(f"Loaded {len(rag.documents)} document representations\n")

    # Example queries
    queries = [
        "What is the price of the Dell XPS 15?",
        "Which laptops have 16GB RAM?",
        "Tell me about the warranty policy"
    ]

    for query in queries:
        print(f"Q: {query}")
        result = rag.query(query)
        print(f"A: {result['answer'][:100]}...")
        print(f"Sources: {len(result['sources'])} documents")
        print(f"Confidence: {result['confidence']:.2f}\n")

if __name__ == "__main__":
    demo()
