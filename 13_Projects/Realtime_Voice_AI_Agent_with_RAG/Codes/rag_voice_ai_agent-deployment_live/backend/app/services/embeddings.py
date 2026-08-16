from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings

class EmbeddingService:

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )     

    def split_text(self, text:str)->List[str]:
        if not text or not text.strip():
            return []
        
        chunks = self.text_splitter.split_text(text)
        return chunks

    def embed_text(self,text:str)->List[float]:
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")
        
        embedding = self.embeddings.embed_query(text)
        return embedding

    def embed_texts(self,texts:List[str])->List[List[float]]:
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return []
        
        embeddings = self.embeddings.embed_documents(valid_texts)
        return embeddings
