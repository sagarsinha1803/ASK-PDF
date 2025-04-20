from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyMuPDFLoader
import tiktoken

class PDFLoader:
    def __init__(self):
        self.file_path = os.getenv("FILE_PATH")

    def load_document(self, pdf):
        loader = PyMuPDFLoader(file_path=pdf)
        doc = loader.load()
        return doc

    def get_all_pdf_path(self, data_directory):
        pdfs = []
        for root, _, files in os.walk(data_directory):
            for file in files:
                if file.endswith('.pdf'):
                    pdfs.append(os.path.join(root, file))
        return pdfs
    
    def load_all_pdf(self, pdfs):
        docs = []
        for pdf in pdfs:
            doc = self.load_document(pdf)
            docs.extend(doc)
        return docs
    
    def get_full_content(self, docs):
        return '\n\n'.join([doc.page_content for doc in docs])
    
    def get_context_token(content):
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        return len(encoding.encode(content))
    
    def get_context(self):
        pdfs = self.get_all_pdf_path(self.file_path)
        docs = self.load_all_pdf(pdfs)
        context = self.get_full_content(docs)
        return context
