import os
import httpx
from typing import List, Dict, Optional
from fastapi import HTTPException
from solders.pubkey import Pubkey
from solders.signature import Signature
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

class SolanaRPC:
    def __init__(self):
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.client = AsyncClient(self.rpc_url)
    
    async def get_token_price(self, token_address: str) -> Dict:
        """Get current token price from on-chain data"""
        try:
            # This would use actual price oracle or DEX pool data
            # Simplified for example purposes
            return {
                "price_usd": 0.0,
                "price_change_24h": 0.0,
                "volume_24h": 0.0,
                "liquidity_usd": 0.0
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch token price: {str(e)}"
            )
    
    async def get_token_transactions(
        self, 
        token_address: str, 
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict]:
        """Get recent transactions for a token"""
        try:
            # Convert token address to Pubkey
            mint_pubkey = Pubkey.from_string(token_address)
            
            # Get signatures for token
            sigs = await self.client.get_signatures_for_address(
                mint_pubkey,
                limit=limit
            )
            
            # Get full transactions
            txs = []
            for sig in sigs.value:
                tx = await self.client.get_transaction(
                    sig.signature,
                    encoding="jsonParsed",
                    commitment=Confirmed
                )
                if tx.value:
                    txs.append(self._parse_transaction(tx.value, token_address))
            
            return txs
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch token transactions: {str(e)}"
            )
    
    def _parse_transaction(self, tx, token_address: str) -> Dict:
        """Parse Solana transaction into our format"""
        # Simplified parsing - real implementation would extract more details
        return {
            "tx_hash": str(tx.transaction.signatures[0]),
            "block_time": tx.block_time,
            "token_address": token_address,
            "from": str(tx.transaction.message.account_keys[0]),
            "to": str(tx.transaction.message.account_keys[1]),
            "amount": 0,  # Would parse actual amount from instruction data
            "fee": tx.meta.fee
        }