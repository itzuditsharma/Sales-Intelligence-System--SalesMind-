from .visualize_graph import visualize_graph
from langchain_core.documents import Document

async def create_graph(org, graph_transformer):
    with open(f"KnowledgeGraph/organisations/{org}.txt", "r", encoding="utf-8") as file:
        text = file.read()

    documents = [Document(page_content=text)]
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)

    # Keep only Person ↔ Client relationships
    for doc in graph_documents:
        doc.relationships = [
            r for r in doc.relationships
            if (r.source.type == "Person" and r.target.type == "Client") 
            #    (r.source.type == "Client" and r.target.type == "Person")
        ]

    print(f"Nodes: {graph_documents[0].nodes}")
    print(f"Relationships: {graph_documents[0].relationships}")

    visualize_graph(graph_documents, path="/home/coewdl/BACKUP/SalesMind/salesmind_app/static/salesmind_app/data/KGImages", org = org)
