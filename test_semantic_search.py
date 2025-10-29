"""
Test script to verify ChromaDB semantic search is working
"""

import sys
from pathlib import Path
import pandas as pd
import json

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))
from vector_store import HybridVectorStore

def load_data():
    """Load all data sources"""
    data = {
        'products': [],
        'faqs': []
    }

    # Load product catalog
    csv_path = Path("data/raw/csvs/product_catalog.csv")
    if csv_path.exists():
        data['products'] = pd.read_csv(csv_path).to_dict('records')

    # Load FAQs
    faq_path = Path("data/raw/text/faqs.json")
    if faq_path.exists():
        with open(faq_path, 'r') as f:
            faq_data = json.load(f)
            data['faqs'] = faq_data.get('faqs', [])

    return data

def test_semantic_search():
    """Test semantic search capabilities"""
    print("=" * 80)
    print("TESTING CHROMADB HYBRID SEARCH")
    print("=" * 80)

    # Load data
    print("\n1. Loading data...")
    data = load_data()
    print(f"   ✓ Loaded {len(data['products'])} products")
    print(f"   ✓ Loaded {len(data['faqs'])} FAQs")

    # Build index
    print("\n2. Building hybrid search index...")
    documents = []
    doc_metadata = []

    for product in data['products']:
        text = f"{product['model']} {product['category']} {product['brand']} "
        text += f"{product.get('processor', '')} {product.get('ram_gb', '')}GB RAM "
        text += f"{product.get('storage_gb', '')}GB storage ${product.get('price_usd', '')}"
        documents.append(text)
        doc_metadata.append({'type': 'product', 'data': product})

    for faq in data['faqs']:
        text = f"{faq['question']} {faq['answer']}"
        documents.append(text)
        doc_metadata.append({'type': 'faq', 'data': faq})

    hybrid_store = HybridVectorStore(collection_name="test_rag", persist_directory="./test_chroma_db")

    # Clear existing data for fresh test
    hybrid_store.vector_store.clear()
    hybrid_store.build_index(documents, doc_metadata)

    stats = hybrid_store.get_stats()
    print(f"   ✓ Vector embeddings: {stats['vector_count']}")
    print(f"   ✓ BM25 documents: {stats['bm25_count']}")

    # Test queries
    print("\n3. Testing semantic search queries...")
    print("-" * 80)

    test_queries = [
        ("affordable laptop for students", "Should find budget laptops"),
        ("high performance gaming machine", "Should find gaming laptops/desktops"),
        ("phone with best camera quality", "Should find phones with good cameras"),
        ("how to return a product", "Should find return policy FAQ"),
        ("budget device under 500", "Should find cheap products"),
    ]

    for query, description in test_queries:
        print(f"\nQuery: '{query}'")
        print(f"Expected: {description}")
        print()

        # Test with different alpha values
        for alpha in [0.0, 0.5, 1.0]:
            mode = "BM25 only" if alpha == 0.0 else ("Semantic only" if alpha == 1.0 else "Hybrid")
            results = hybrid_store.hybrid_search(query, top_k=3, alpha=alpha)

            if results:
                print(f"  [{mode:15s}] Top result (score={results[0]['score']:.3f}):")
                if results[0]['metadata']['type'] == 'product':
                    product = results[0]['metadata']['data']
                    print(f"                   → {product['model']} - ${product.get('price_usd', 'N/A')}")
                else:
                    faq = results[0]['metadata']['data']
                    print(f"                   → FAQ: {faq['question'][:60]}...")
            else:
                print(f"  [{mode:15s}] No results found")

        print()

    print("=" * 80)
    print("✅ SEMANTIC SEARCH TEST COMPLETE!")
    print("=" * 80)
    print("\nKey observations:")
    print("- Semantic search (alpha=1.0) understands intent and meaning")
    print("- BM25 search (alpha=0.0) relies on exact keyword matching")
    print("- Hybrid search (alpha=0.5) combines both approaches")
    print("\n💡 Try adjusting the semantic weight slider in the Streamlit app!")

if __name__ == "__main__":
    test_semantic_search()
