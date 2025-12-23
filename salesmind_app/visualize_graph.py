import os
import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(graph_documents, path, org):
    """
    Save a knowledge graph as PNG directly (no HTML dependency).
    """
    os.makedirs(path, exist_ok=True)
    output_file_png = os.path.join(path, f"{org}.png")

    nodes = graph_documents[0].nodes
    relationships = graph_documents[0].relationships

    # Build NetworkX graph
    G = nx.DiGraph()

    for node in nodes:
        G.add_node(node.id, type=node.type)

    for rel in relationships:
        if rel.source.id in G.nodes and rel.target.id in G.nodes:
            G.add_edge(rel.source.id, rel.target.id, type=rel.type)

    # Set positions using spring layout (similar to force-directed)
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # Node colors based on type
    node_types = list(set(nx.get_node_attributes(G, 'type').values()))
    color_map = {t: plt.cm.tab20(i) for i, t in enumerate(node_types)}
    node_colors = [color_map[G.nodes[n]['type']] for n in G.nodes]

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800)
    # Draw edges
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='gray')
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='white')

    edge_labels = nx.get_edge_attributes(G, 'type')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='white', font_size=5, bbox=dict(facecolor='none', edgecolor='none', pad=0))

    # Create legend for node types
    for t, color in color_map.items():
        plt.scatter([], [], c=[color], label=t)
    plt.legend(scatterpoints=1, fontsize=8)

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file_png, dpi=300, bbox_inches='tight', facecolor='#222222')
    plt.close()
    print(f"Knowledge graph saved as PNG: {os.path.abspath(output_file_png)}")

