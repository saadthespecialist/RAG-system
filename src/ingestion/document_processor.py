"""
Document Processing with Multi-Representation
Processes PDFs, CSVs, and text files with multiple embedding strategies
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, CSVLoader, TextLoader
from langchain.docstore.document import Document
import pypdf2
import re

class MultiRepresentationProcessor:
    """Process documents with multiple representations"""

    def __init__(self, chunk_size=512, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def process_pdf(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        Process PDF with multiple representations:
        1. Full document
        2. Page-level chunks
        3. Extracted tables
        4. Summary (if long)
        """
        representations = []

        try:
            # Load PDF
            loader = PyPDFLoader(str(filepath))
            pages = loader.load()

            full_text = "\n\n".join([p.page_content for p in pages])

            # Representation 1: Full document embedding
            representations.append({
                "doc_id": filepath.stem,
                "type": "full_document",
                "content": full_text[:2000],  # First 2000 chars as summary
                "metadata": {
                    "source": str(filepath),
                    "doc_type": "pdf",
                    "total_pages": len(pages)
                }
            })

            # Representation 2: Page-level chunks
            for idx, page in enumerate(pages):
                chunks = self.text_splitter.split_text(page.page_content)
                for chunk_idx, chunk in enumerate(chunks):
                    representations.append({
                        "doc_id": f"{filepath.stem}_page{idx+1}_chunk{chunk_idx}",
                        "type": "page_chunk",
                        "content": chunk,
                        "metadata": {
                            "source": str(filepath),
                            "doc_type": "pdf",
                            "page": idx + 1,
                            "chunk_id": chunk_idx,
                            "parent_doc": filepath.stem
                        }
                    })

            # Representation 3: Extract key facts/propositions
            facts = self._extract_facts(full_text)
            for fact_idx, fact in enumerate(facts):
                representations.append({
                    "doc_id": f"{filepath.stem}_fact{fact_idx}",
                    "type": "fact",
                    "content": fact,
                    "metadata": {
                        "source": str(filepath),
                        "doc_type": "pdf",
                        "parent_doc": filepath.stem
                    }
                })

        except Exception as e:
            print(f"Error processing PDF {filepath}: {e}")

        return representations

    def process_csv(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        Process CSV with table-aware representations:
        1. Full table summary
        2. Row-level embeddings
        3. Column statistics
        """
        representations = []

        try:
            df = pd.read_csv(filepath)

            # Representation 1: Table summary
            summary = f"Table: {filepath.stem}\n"
            summary += f"Columns: {', '.join(df.columns.tolist())}\n"
            summary += f"Total Rows: {len(df)}\n"
            summary += f"Sample Data:\n{df.head(3).to_string()}"

            representations.append({
                "doc_id": f"{filepath.stem}_summary",
                "type": "table_summary",
                "content": summary,
                "metadata": {
                    "source": str(filepath),
                    "doc_type": "csv",
                    "columns": df.columns.tolist(),
                    "row_count": len(df)
                }
            })

            # Representation 2: Row-level embeddings (for product specs, pricing)
            for idx, row in df.iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items()])
                representations.append({
                    "doc_id": f"{filepath.stem}_row{idx}",
                    "type": "table_row",
                    "content": row_text,
                    "metadata": {
                        "source": str(filepath),
                        "doc_type": "csv",
                        "row_index": idx,
                        "parent_table": filepath.stem,
                        "row_data": row.to_dict()
                    }
                })

            # Representation 3: Column-specific insights (for numeric columns)
            numeric_cols = df.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                stats_text = f"Column: {col}\n"
                stats_text += f"Min: {df[col].min()}, Max: {df[col].max()}, "
                stats_text += f"Mean: {df[col].mean():.2f}, Median: {df[col].median()}"

                representations.append({
                    "doc_id": f"{filepath.stem}_col_{col}",
                    "type": "column_stats",
                    "content": stats_text,
                    "metadata": {
                        "source": str(filepath),
                        "doc_type": "csv",
                        "column": col,
                        "parent_table": filepath.stem
                    }
                })

        except Exception as e:
            print(f"Error processing CSV {filepath}: {e}")

        return representations

    def process_json(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        Process JSON files (e.g., FAQs)
        """
        representations = []

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Handle FAQs
            if "faqs" in data:
                for idx, faq in enumerate(data["faqs"]):
                    # Q&A pair as single document
                    qa_text = f"Question: {faq['question']}\nAnswer: {faq['answer']}"
                    representations.append({
                        "doc_id": f"faq_{idx}",
                        "type": "faq",
                        "content": qa_text,
                        "metadata": {
                            "source": str(filepath),
                            "doc_type": "faq",
                            "question": faq['question'],
                            "answer": faq['answer']
                        }
                    })

            # Handle product catalog JSON
            elif isinstance(data, list):
                for idx, item in enumerate(data):
                    item_text = json.dumps(item, indent=2)
                    representations.append({
                        "doc_id": f"{filepath.stem}_{idx}",
                        "type": "json_item",
                        "content": item_text,
                        "metadata": {
                            "source": str(filepath),
                            "doc_type": "json",
                            "item_index": idx
                        }
                    })

        except Exception as e:
            print(f"Error processing JSON {filepath}: {e}")

        return representations

    def _extract_facts(self, text: str, max_facts: int = 10) -> List[str]:
        """Extract key facts/propositions from text"""
        # Simple sentence extraction (in production, use LLM for better extraction)
        sentences = re.split(r'[.!?]+', text)
        facts = []

        for sent in sentences:
            sent = sent.strip()
            # Filter for informative sentences
            if len(sent) > 30 and len(sent) < 200:
                if any(keyword in sent.lower() for keyword in ['features', 'includes', 'provides', 'offers', 'supports']):
                    facts.append(sent)
                    if len(facts) >= max_facts:
                        break

        return facts

    def process_directory(self, data_dir: Path) -> List[Dict[str, Any]]:
        """Process all documents in directory"""
        all_representations = []

        # Process PDFs
        pdf_dir = data_dir / "pdfs"
        if pdf_dir.exists():
            for pdf_file in pdf_dir.glob("*.pdf"):
                reps = self.process_pdf(pdf_file)
                all_representations.extend(reps)

        # Process CSVs
        csv_dir = data_dir / "csvs"
        if csv_dir.exists():
            for csv_file in csv_dir.glob("*.csv"):
                reps = self.process_csv(csv_file)
                all_representations.extend(reps)

        # Process JSON
        text_dir = data_dir / "text"
        if text_dir.exists():
            for json_file in text_dir.glob("*.json"):
                reps = self.process_json(json_file)
                all_representations.extend(reps)

        return all_representations


def main():
    """Process all documents"""
    print("Processing documents with multi-representation...")

    processor = MultiRepresentationProcessor()
    representations = processor.process_directory(Path("data/raw"))

    print(f"\n✓ Processed {len(representations)} document representations")

    # Save processed representations
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "representations.json", 'w') as f:
        json.dump(representations, f, indent=2)

    print(f"Saved to: {output_dir / 'representations.json'}")

if __name__ == "__main__":
    main()
