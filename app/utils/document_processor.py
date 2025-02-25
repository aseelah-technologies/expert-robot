import os
from PyPDF2 import PdfReader
from langdetect import detect
from typing import List, Dict
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class DocumentProcessor:
    def __init__(self, documents_path: str, chunk_size: int = 500):
        self.documents_path = documents_path
        self.chunk_size = chunk_size
        self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of approximately equal size"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space

            if current_size >= self.chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def create_embeddings(self, text: str) -> List[float]:
        """Create embeddings for text using sentence-transformers"""
        return self.model.encode(text).tolist()

    def process_document(self, file_path: str) -> Dict:
        """Process a single document and create chunks with embeddings"""
        try:
            # Read PDF
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            # Detect language
            language = detect(text)

            # Create chunks
            chunks = self.chunk_text(text)
            
            # Create embeddings for chunks
            chunk_data = []
            for idx, chunk in enumerate(chunks):
                embedding = self.create_embeddings(chunk)
                chunk_data.append({
                    'content': chunk,
                    'embedding': embedding,
                    'chunk_index': idx
                })

            return {
                'filename': os.path.basename(file_path),
                'content': text,
                'language': language,
                'chunks': chunk_data
            }

        except Exception as e:
            print(f"Error processing document {file_path}: {str(e)}")
            return None

    def save_to_database(self, doc_data: Dict, db_session):
        """Save processed document and chunks to database"""
        from app.models.document_models import Document, DocumentChunk

        # Create document record
        doc = Document(
            filename=doc_data['filename'],
            content=doc_data['content'],
            language=doc_data['language']
        )
        db_session.add(doc)
        db_session.flush()  # Get doc.id

        # Create chunk records
        for chunk_data in doc_data['chunks']:
            chunk = DocumentChunk(
                document_id=doc.id,
                content=chunk_data['content'],
                embedding=json.dumps(chunk_data['embedding']),
                chunk_index=chunk_data['chunk_index']
            )
            db_session.add(chunk)

        db_session.commit()