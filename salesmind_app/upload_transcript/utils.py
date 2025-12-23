import os
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

        
    