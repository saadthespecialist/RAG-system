"""
Master script to generate all synthetic data
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_generation.product_generator import ProductDataGenerator
from data_generation.pdf_generator import PDFManualGenerator

def main():
    """Generate complete synthetic dataset"""
    print("=" * 60)
    print("SYNTHETIC DATA GENERATION FOR RAG SYSTEM")
    print("=" * 60)

    # Step 1: Generate product catalog
    print("\n[1/3] Generating product catalog...")
    product_gen = ProductDataGenerator()
    products = product_gen.generate_catalog(num_products=150)
    product_gen.save_as_csv(products)
    product_gen.save_as_json(products)

    # Step 2: Generate pricing and FAQs
    print("\n[2/3] Generating pricing and FAQ data...")
    product_gen.generate_pricing_table(products)
    product_gen.generate_faqs()

    # Step 3: Generate PDF manuals
    print("\n[3/3] Generating PDF product manuals...")
    pdf_gen = PDFManualGenerator()
    pdf_gen.generate_all_manuals(products[:30])  # First 30 products

    print("\n" + "=" * 60)
    print("✓ DATA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\nGenerated Files:")
    print(f"  • Product Catalog: data/raw/csvs/product_catalog.csv")
    print(f"  • Product JSON: data/raw/text/product_catalog.json")
    print(f"  • Pricing Data: data/raw/csvs/pricing.csv")
    print(f"  • FAQs: data/raw/text/faqs.json")
    print(f"  • PDF Manuals: data/raw/pdfs/ (30 files)")
    print(f"\nTotal Products: {len(products)}")
    print(f"Ready for RAG ingestion!")

if __name__ == "__main__":
    main()
