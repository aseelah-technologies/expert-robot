import unittest
from app.utils.document_processor import DocumentProcessor
import os

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor("./test_documents")
        
    def test_chunk_text(self):
        text = "This is a test " * 100
        chunks = self.processor.chunk_text(text)
        self.assertTrue(all(len(chunk) <= 500 for chunk in chunks))
        
    # Add more tests...