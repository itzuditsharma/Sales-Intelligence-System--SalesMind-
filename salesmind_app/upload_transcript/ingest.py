import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embedding = OpenAIEmbeddings()
_faiss_db = None

APP_DIR = os.path.dirname(os.path.abspath(__file__))

def get_faiss_db():
    global _faiss_db
    file_path = os.path.join(APP_DIR, 'faiss_index')
    print("file_path:", file_path)
    if _faiss_db is None and os.path.exists(file_path + 'index.faiss'):
        _faiss_db = FAISS.load_local(file_path, embedding, allow_dangerous_deserialization=True)
    return _faiss_db

def set_faiss_db(db):
    global _faiss_db
    _faiss_db = db
    
def save_faiss_db(path):
    if _faiss_db:
        _faiss_db.save_local(path)

        
def ingest_transcript(path: str):
    """Ingests a transcript from a given file path into the vector store."""
    print("path ingest file:", path)
    faiss_db = get_faiss_db()

    if not os.path.exists(path):
        return f" File not found: {path} — cwd = {os.getcwd()}"

    try:
        loader = TextLoader(path, encoding="utf-8")
        docs = loader.load()
    except Exception as e:
        return f" Error loading {path}: {str(e)}"

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    if faiss_db is None:
        embedding = OpenAIEmbeddings()
        faiss_db = FAISS.from_documents(chunks, embedding)
    else:
        faiss_db.add_documents(chunks)

    set_faiss_db(faiss_db)
    save_faiss_db("faiss_index")

    print(f" Ingested {len(chunks)} chunks from {path}")