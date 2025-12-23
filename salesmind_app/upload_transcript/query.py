from langchain_core.tools import tool
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from django.conf import settings
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType

embedding = OpenAIEmbeddings()
_faiss_db = None
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def init_agent(tools, llm, verbose=True):
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False
    )

def get_faiss_db():
    global _faiss_db
    file_path = os.path.join(settings.BASE_DIR, 'faiss_index')
    # print("file_path:", file_path)
    if _faiss_db is None and os.path.exists(file_path + '/index.faiss'):
        _faiss_db = FAISS.load_local(file_path, embedding, allow_dangerous_deserialization=True)
    return _faiss_db

def create_document_chain():
    llm = ChatOpenAI(model_name="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_template("""
    You are a helpful assistant. Use the below call excerpts to answer the user's question. Mention specific excerpts in your answer.
    If you don't know the answer, say I don't have the answer.
    <context>
    {context}
    </context>

    Question: {input}
    Answer:
    """)
    return create_stuff_documents_chain(llm, prompt), llm


document_chain, _ = create_document_chain()

@tool
def query_transcripts(question: str) -> str:
    """Answers a question by querying the ingested transcripts."""
    faiss_db = get_faiss_db()
    if faiss_db is None:
        return "No transcripts ingested yet. Please ingest first."

    retrieved_docs = faiss_db.similarity_search(question, k=4)

    response = document_chain.invoke({
        "input": question,
        "context": [doc for doc in retrieved_docs]
    })

    return f"{response}\n"


def create_document_chain_report():
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)
    prompt = ChatPromptTemplate.from_template("""
    You are an expert business analyst. You will be given call excerpts or sales transcripts.

    <context>
    {context}
    </context>

    Based on the above context, generate a comprehensive, detailed report covering:
    - The main discussion points
    - Key clients or deals mentioned
    - Any competitor references
    - Action items, follow-ups, or strategic decisions
    - Summary of tone and overall sentiment

    Your output should be a well-structured written report in paragraphs — 
    without bullet points, without saying “Here is the report”, and without any metadata or formatting tags.
    """)
    return create_stuff_documents_chain(llm, prompt), llm

document_chain_report, _ = create_document_chain_report()

@tool
def generate_report(question: str) -> str:
    """Generate a report by querying the ingested transcripts."""
    faiss_db = get_faiss_db()
    if faiss_db is None:
        return "No transcripts ingested yet. Please ingest first."

    retrieved_docs = faiss_db.similarity_search(question, k=4)

    response = document_chain_report.invoke({
        "input": question,
        "context": [doc for doc in retrieved_docs]
    })

    snippets = "\n\n".join([
        f"[{doc.metadata.get('source', 'unknown')}]:\n{doc.page_content.strip()[:300]}..."
        for doc in retrieved_docs
    ])

    return f"Answer:\n{response}\n\n Context:\n{snippets}"