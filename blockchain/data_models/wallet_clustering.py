import networkx as nx
import community as community_louvain
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class WalletCluster:
    wallets: List[str]
    risk_score: float
    common_tokens: List[str]
    cluster_type: str  # "SERIAL_DEPLOYER", "PUMP_GROUP", etc.

class WalletGraphAnalyzer:
    def __init__(self, transactions_df: pd.DataFrame):
        """
        Initialize with transaction data from SQL query results
        Columns needed: from_address, to_address, token_address, amount_usd, block_time
        """
        self.graph = nx.MultiDiGraph()
        self.transactions = transactions_df
        self.clusters: List[WalletCluster] = []
    
    def build_transaction_graph(self, time_window_hours: int = 24):
        """Convert transactions to temporal graph edges"""
        time_filtered = self.transactions[
            self.transactions['block_time'] >= pd.Timestamp.now() - pd.Timedelta(hours=time_window_hours)
        ]
        
        for _, tx in time_filtered.iterrows():
            self.graph.add_edge(
                tx['from_address'],
                tx['to_address'],
                token=tx['token_address'],
                amount=tx['amount_usd'],
                time=tx['block_time']
            )
    
    def detect_clusters(self) -> List[WalletCluster]:
        """Run Louvain community detection and risk scoring"""
        undirected = self.graph.to_undirected()
        partition = community_louvain.best_partition(undirected)
        
        communities: Dict[int, List[str]] = {}
        for node, comm_id in partition.items():
            communities.setdefault(comm_id, []).append(node)
        
        for comm_id, wallets in communities.items():
            if len(wallets) < 2:  # Skip single-wallet "clusters"
                continue
                
            risk_score = self._calculate_cluster_risk(wallets)
            cluster_type = self._classify_cluster(wallets)
            
            self.clusters.append(WalletCluster(
                wallets=wallets,
                risk_score=risk_score,
                common_tokens=self._get_common_tokens(wallets),
                cluster_type=cluster_type
            ))
        
        return sorted(self.clusters, key=lambda x: x.risk_score, reverse=True)
    
    def _calculate_cluster_risk(self, wallets: List[str]) -> float:
        """Score based on transaction patterns"""
        wallet_subgraph = self.graph.subgraph(wallets)
        total_volume = sum(data['amount'] for _, _, data in wallet_subgraph.edges(data=True))
        
        # Risk factors
        internal_tx_ratio = len(wallet_subgraph.edges()) / len(self.graph.edges())
        token_concentration = len(set(data['token'] for _, _, data in wallet_subgraph.edges(data=True)))
        
        return (internal_tx_ratio * 0.6) + (token_concentration * 0.4)
    
    def _classify_cluster(self, wallets: List[str]) -> str:
        """Determine cluster type based on behavior"""
        deployer_count = sum(1 for w in wallets if w.startswith('DEPLOYER_'))  # Assuming tagged wallets
        if deployer_count > 3:
            return "SERIAL_DEPLOYER_NETWORK"
        
        # Add more classification logic here
        return "SUSPECT_TRADING_RING"
    
    def _get_common_tokens(self, wallets: List[str]) -> List[str]:
        """Get tokens most frequently traded in cluster"""
        wallet_txs = [data['token'] for _, _, data in self.graph.subgraph(wallets).edges(data=True)]
        return pd.Series(wallet_txs).value_counts().head(3).index.tolist()