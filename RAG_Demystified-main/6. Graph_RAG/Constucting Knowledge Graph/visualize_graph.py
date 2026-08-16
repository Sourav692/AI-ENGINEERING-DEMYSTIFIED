import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st

# Function to build and plot the knowledge graph
def plot_knowledge_graph(entities, relationships):
    G = nx.DiGraph()
    
    # Add relationships as edges to the graph
    for entity1, relationship, entity2 in relationships:
        G.add_edge(entity1, entity2, label=relationship)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 8))
    
    # Draw the graph with labels
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=5000, edge_color='black', font_size=10)
    
    # Add edge labels
    edge_labels = {(entity1, entity2): relationship for entity1, relationship, entity2 in relationships}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    
    plt.title("Knowledge Graph")
    st.pyplot(plt)