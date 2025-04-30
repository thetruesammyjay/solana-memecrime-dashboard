import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd

def generate_wallet_graph(transactions: pd.DataFrame, output_file: str):
    """
    Generate interactive wallet transaction graph
    """
    G = nx.DiGraph()
    
    # Add nodes and edges
    for _, tx in transactions.iterrows():
        G.add_node(tx['from'], size=10, title=tx['from'])
        G.add_node(tx['to'], size=10, title=tx['to'])
        G.add_edge(tx['from'], tx['to'], value=tx['amount_usd'], title=f"{tx['amount_usd']} USD")
    
    # Generate visualization
    net = Network(height="750px", width="100%", directed=True)
    net.from_nx(G)
    
    # Save as HTML
    net.save_graph(output_file)
    print(f"Graph saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    sample_data = pd.DataFrame([{
        'from': 'walletA',
        'to': 'walletB',
        'amount_usd': 1000
    }])
    generate_wallet_graph(sample_data, "wallet_graph.html")