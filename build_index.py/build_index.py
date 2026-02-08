# build_index.py
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

# Define the paths
KNOWLEDGE_BASE_DIR = "knowledge_base"
DB_DIR = "chroma_db"

print("Loading documents from the knowledge base...")
loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.txt")
documents = loader.load()

print(f"Splitting {len(documents)} document(s) into chunks...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

print("Creating embeddings and building the vector store... (This may take a minute)")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Create and persist the ChromaDB database
vectorstore = Chroma.from_documents(
    documents=texts, 
    embedding=embeddings, 
    persist_directory=DB_DIR
)

print(f"--- Index built successfully! ---")
print(f"Knowledge from {len(documents)} file(s) has been indexed in the '{DB_DIR}' folder.")