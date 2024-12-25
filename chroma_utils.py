from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000 , chunk_overlap=200)
embedding_function = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)
print("Embedding function loaded")  

def load_and_split_document(file_path:str)->List[Document]:
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)    
    elif file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith(".html"):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise Exception("Unsupported file format:{file_path}")
    
    document = loader.load()
    return text_splitter.split_documents(document)
    
def index_document_to_chroma(file_path:str , file_id:int):
    try:
        splits = load_and_split_document(file_path)
        
        for split in splits:
            split.metadata["file_id"] = file_id
            
        vectorstore.add_documents(splits)
        
        return True
    
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False
    
def delete_doc_from_chroma(file_id:int)-> bool:
    try:
        docs = vectorstore.get(where={"file_id":file_id})
        print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")
        
        vectorstore._collection.delete(where={"file_id":file_id})
        print(f"Deleted all documents with file_id {file_id}")
        
        return True
    
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False