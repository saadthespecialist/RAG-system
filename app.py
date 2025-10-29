"""
Streamlit Web Interface for RAG System Demo
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))
from vector_store import HybridVectorStore

# Page config
st.set_page_config(
    page_title="Advanced RAG System Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }

    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #667eea30;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Result cards */
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Product card styling */
    .product-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    /* FAQ card styling */
    .faq-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    /* Score badge */
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    /* Stats box */
    .stats-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }

    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: transform 0.2s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea15 0%, #764ba215 100%);
    }

    /* Search box styling */
    .stTextInput>div>div>input {
        border: 2px solid #667eea30;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
    }

    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }

    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 8px;
        font-weight: 600;
    }

    /* Info box */
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Warning box */
    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Success box */
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all data sources"""
    data = {
        'products': [],
        'pricing': [],
        'faqs': []
    }

    # Load product catalog
    csv_path = Path("data/raw/csvs/product_catalog.csv")
    if csv_path.exists():
        data['products'] = pd.read_csv(csv_path).to_dict('records')

    # Load pricing
    pricing_path = Path("data/raw/csvs/pricing.csv")
    if pricing_path.exists():
        data['pricing'] = pd.read_csv(pricing_path).to_dict('records')

    # Load FAQs
    faq_path = Path("data/raw/text/faqs.json")
    if faq_path.exists():
        with open(faq_path, 'r') as f:
            faq_data = json.load(f)
            data['faqs'] = faq_data.get('faqs', [])

    return data

@st.cache_resource
def build_search_index(data):
    """Build hybrid search index with ChromaDB + BM25"""
    # Combine all searchable text
    documents = []
    doc_metadata = []

    # Add products
    for product in data['products']:
        text = f"{product['model']} {product['category']} {product['brand']} "
        text += f"{product.get('processor', '')} {product.get('ram_gb', '')}GB RAM "
        text += f"{product.get('storage_gb', '')}GB storage ${product.get('price_usd', '')}"
        documents.append(text)
        doc_metadata.append({'type': 'product', 'data': product})

    # Add FAQs
    for faq in data['faqs']:
        text = f"{faq['question']} {faq['answer']}"
        documents.append(text)
        doc_metadata.append({'type': 'faq', 'data': faq})

    # Build hybrid index with ChromaDB vector store + BM25
    hybrid_store = HybridVectorStore(collection_name="rag_products", persist_directory="./chroma_db")

    # Check if index already exists
    if hybrid_store.get_stats()['vector_count'] == 0:
        # Build new index
        hybrid_store.build_index(documents, doc_metadata)

    return hybrid_store

def search(query, hybrid_store, top_k=5, alpha=0.7):
    """Search using hybrid ChromaDB + BM25"""
    return hybrid_store.hybrid_search(query, top_k=top_k, alpha=alpha)

def format_product(product):
    """Format product for display"""
    return f"""
**{product['model']}**
- **Category**: {product['category']}
- **Processor**: {product.get('processor', 'N/A')}
- **RAM**: {product.get('ram_gb', 'N/A')} GB
- **Storage**: {product.get('storage_gb', 'N/A')} GB
- **Price**: ${product.get('price_usd', 'N/A')}
- **Rating**: {product.get('rating', 'N/A')}/5.0
- **In Stock**: {'✅ Yes' if product.get('in_stock') else '❌ No'}
"""

# Main app header
st.markdown('<h1 class="main-title">🤖 Advanced RAG System</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Intelligent Sales & Product Knowledge Assistant</p>', unsafe_allow_html=True)

# Feature highlights
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="stats-box"><h3 style="margin:0; color:white;">150</h3><p style="margin:0; color:white;">Products</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stats-box"><h3 style="margin:0; color:white;">15</h3><p style="margin:0; color:white;">FAQs</p></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="stats-box"><h3 style="margin:0; color:white;">Hybrid</h3><p style="margin:0; color:white;">Search</p></div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="stats-box"><h3 style="margin:0; color:white;">ChromaDB</h3><p style="margin:0; color:white;">Vector Store</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Feature cards
st.markdown("""
<div class="feature-card">
    <h3 style="margin-top:0; color:#667eea;">🚀 Key Features</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div>
            <p><strong>🔍 Hybrid Search</strong><br/>
            Combines ChromaDB semantic vectors with BM25 keyword search</p>
        </div>
        <div>
            <p><strong>🧠 Semantic Understanding</strong><br/>
            Understands query intent, not just keywords</p>
        </div>
        <div>
            <p><strong>⚡ Fast Retrieval</strong><br/>
            Persistent vector storage for instant results</p>
        </div>
        <div>
            <p><strong>🎯 Multi-Modal Data</strong><br/>
            Products, pricing, FAQs, and manuals</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("Loading product catalog and building search index..."):
    data = load_data()
    hybrid_store = build_search_index(data)

# Sidebar stats
st.sidebar.title("📊 Data Statistics")
st.sidebar.metric("Total Products", len(data['products']))
st.sidebar.metric("FAQs", len(data['faqs']))
st.sidebar.metric("Pricing Entries", len(data['pricing']))

# Index stats
stats = hybrid_store.get_stats()
st.sidebar.divider()
st.sidebar.subheader("🔍 Search Index")
st.sidebar.metric("Vector Embeddings", stats['vector_count'])
st.sidebar.caption("🤖 Using ChromaDB + BM25 Hybrid Search")

# Search settings
st.sidebar.divider()
st.sidebar.subheader("⚙️ Search Settings")
alpha = st.sidebar.slider(
    "Semantic Weight",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="Balance between semantic (ChromaDB) and keyword (BM25) search. Higher = more semantic."
)

# Query input section
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("## 💬 Ask Your Question")

query = st.text_input(
    "Search for products, pricing, or information:",
    placeholder="e.g., 'Which laptops have 16GB RAM?' or 'What is the return policy?'",
    label_visibility="collapsed"
)

# Example queries with better styling
st.markdown("**✨ Try these examples:**")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("💻 Gaming Laptops", use_container_width=True):
        query = "high performance gaming laptops"
with col2:
    if st.button("📱 Best Camera Phone", use_container_width=True):
        query = "phone with best camera quality"
with col3:
    if st.button("💰 Budget Options", use_container_width=True):
        query = "affordable devices under 500"
with col4:
    if st.button("❓ Return Policy", use_container_width=True):
        query = "return policy warranty"

if query:
    st.markdown("---")
    st.markdown(f"## 🔍 Results for: <span style='color:#667eea;'>*{query}*</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Search with hybrid approach
    with st.spinner("🔎 Searching..."):
        results = search(query, hybrid_store, top_k=5, alpha=alpha)

    if results:
        st.markdown(f'<div class="info-box">📊 Found <strong>{len(results)}</strong> relevant results (semantic weight: {alpha*100:.0f}%)</div>', unsafe_allow_html=True)

        for i, result in enumerate(results, 1):
            metadata_item = result['metadata']

            # Determine card type and color
            if metadata_item['type'] == 'product':
                card_icon = "💻"
                card_type = "Product"
                card_color = "#667eea"
            else:
                card_icon = "❓"
                card_type = "FAQ"
                card_color = "#ff9800"

            with st.expander(f"{card_icon} **Result #{i}** - {card_type} | Relevance: {result['score']:.2%}", expanded=(i==1)):
                # Score badge
                st.markdown(f'<span class="score-badge">🎯 Relevance Score: {result["score"]:.3f}</span>', unsafe_allow_html=True)

                if metadata_item['type'] == 'product':
                    product = metadata_item['data']

                    # Product card with better styling
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)

                    col_a, col_b = st.columns([2, 1])

                    with col_a:
                        st.markdown(f"### {product['model']}")
                        st.markdown(f"**Brand:** {product.get('brand', 'N/A')} | **Category:** {product['category']}")
                        st.markdown("---")

                        # Specs in columns
                        spec_col1, spec_col2 = st.columns(2)
                        with spec_col1:
                            st.markdown(f"**🔧 Processor:** {product.get('processor', 'N/A')}")
                            st.markdown(f"**💾 RAM:** {product.get('ram_gb', 'N/A')} GB")
                        with spec_col2:
                            st.markdown(f"**💽 Storage:** {product.get('storage_gb', 'N/A')} GB")
                            st.markdown(f"**⭐ Rating:** {product.get('rating', 'N/A')}/5.0")

                    with col_b:
                        # Price box
                        price = product.get('price_usd', 'N/A')
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
                            <h2 style="margin:0; color:white;">${price}</h2>
                            <p style="margin:0; color:white;">Current Price</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Stock status
                        if product.get('in_stock'):
                            st.success("✅ In Stock")
                        else:
                            st.error("❌ Out of Stock")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # Show pricing if available
                    pricing_match = next(
                        (p for p in data['pricing'] if p['product_id'] == product['product_id']),
                        None
                    )
                    if pricing_match and pricing_match['discount_percent'] > 0:
                        st.markdown(f"""
                        <div class="success-box">
                            <strong>🎉 SPECIAL OFFER!</strong><br/>
                            Save {pricing_match['discount_percent']}% -
                            Sale Price: <strong>${pricing_match['sale_price_usd']:.2f}</strong>
                        </div>
                        """, unsafe_allow_html=True)

                elif metadata_item['type'] == 'faq':
                    faq = metadata_item['data']

                    # FAQ card with better styling
                    st.markdown('<div class="faq-card">', unsafe_allow_html=True)
                    st.markdown(f"### ❓ {faq['question']}")
                    st.markdown("---")
                    st.markdown(f"**Answer:** {faq['answer']}")
                    st.markdown('</div>', unsafe_allow_html=True)

                # Citation
                st.markdown("---")
                st.caption(f"📄 **Source Type:** {metadata_item['type'].upper()}")

    else:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ No results found</strong><br/>
            Try adjusting your query or search settings in the sidebar.
        </div>
        """, unsafe_allow_html=True)

# Data viewer
with st.expander("📁 Browse All Products"):
    if data['products']:
        df = pd.DataFrame(data['products'])
        st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🚀 Built with Advanced RAG Techniques</p>
    <p><i>Multi-representation retrieval • Hybrid search • Source attribution</i></p>
</div>
""", unsafe_allow_html=True)
