from solana.rpc.api import Client
from solana.publickey import PublicKey
import re

class TokenSniffer:
    def __init__(self, rpc_url: str):
        self.client = Client(rpc_url)
        self.token_pattern = re.compile(r"token.*mint", re.IGNORECASE)
    
    def detect_new_tokens(self, recent_blocks: int = 50):
        """Scan recent blocks for new token creations"""
        latest_slot = self.client.get_slot()['result']
        blocks = range(latest_slot - recent_blocks, latest_slot)
        
        new_tokens = []
        for slot in blocks:
            block = self.client.get_block(slot)['result']
            for tx in block['transactions']:
                if self._is_token_creation(tx):
                    token_data = self._extract_token_data(tx)
                    new_tokens.append(token_data)
        
        return new_tokens
    
    def _is_token_creation(self, tx) -> bool:
        """Heuristic check for token creation"""
        return any(
            self.token_pattern.search(str(log)) 
            for log in tx['meta']['logMessages']
        )
    
    def _extract_token_data(self, tx) -> dict:
        """Extract token metadata from creation transaction"""
        # Implementation would parse transaction logs
        return {
            "token_address": "...",
            "creator": "...",
            "timestamp": "...",
            "initial_supply": 0
        }