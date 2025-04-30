import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
from typing import Dict, List
import matplotlib.pyplot as plt

class TemporalGraphAnalyzer:
    def __init__(self, transactions: pd.DataFrame):
        """
        Initialize with transaction data
        Expected columns: tx_hash, block_time, from_address, to_address, token_address, amount_usd
        """
        self.transactions = transactions
        self.time_windows = [
            ('0-1h', timedelta(hours=1)),
            ('1-6h', timedelta(hours=6)),
            ('6-24h', timedelta(hours=18))
        ]
    
    def analyze_temporal_patterns(self) -> Dict[str, dict]:
        """Analyze graph metrics over time windows"""
        results = {}
        base_time = self.transactions['block_time'].max()
        
        for label, delta in self.time_windows:
            window_start = base_time - delta
            window_txs = self.transactions[
                (self.transactions['block_time'] >= window_start) & 
                (self.transactions['block_time'] <= base_time)
            ]
            
            G = nx.from_pandas_edgelist(
                window_txs,
                source='from_address',
                target='to_address',
                edge_attr=['amount_usd', 'token_address'],
                create_using=nx.DiGraph
            )
            
            metrics = {
                'node_count': len(G.nodes()),
                'edge_count': len(G.edges()),
                'density': nx.density(G),
                'reciprocity': nx.reciprocity(G),
                'centralization': self._calculate_centralization(G),
                'top_tokens': window_txs['token_address'].value_counts().head(3).to_dict()
            }
            
            results[label] = metrics
        
        return results
    
    def _calculate_centralization(self, G: nx.Graph) -> float:
        """Compute degree centralization score"""
        if len(G) == 0:
            return 0.0
        
        degrees = nx.degree_centrality(G)
        max_degree = max(degrees.values())
        centralization = sum(max_degree - d for d in degrees.values()) / (len(G) - 1)
        return centralization
    
    def visualize_evolution(self, temporal_results: Dict[str, dict]):
        """Plot key metrics over time windows"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Node count
        axes[0,0].bar(
            temporal_results.keys(),
            [v['node_count'] for v in temporal_results.values()]
        )
        axes[0,0].set_title('Unique Wallets Over Time')
        
        # Edge count
        axes[0,1].bar(
            temporal_results.keys(),
            [v['edge_count'] for v in temporal_results.values()]
        )
        axes[0,1].set_title('Transaction Count Over Time')
        
        # Centralization
        axes[1,0].plot(
            temporal_results.keys(),
            [v['centralization'] for v in temporal_results.values()],
            marker='o'
        )
        axes[1,0].set_title('Network Centralization')
        
        # Reciprocity
        axes[1,1].plot(
            temporal_results.keys(),
            [v['reciprocity'] for v in temporal_results.values()],
            marker='o'
        )
        axes[1,1].set_title('Transaction Reciprocity')
        
        plt.tight_layout()
        return fig