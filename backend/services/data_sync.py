import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from ..utils.dune_client import DuneClient
from ..utils.solana_rpc import SolanaRPC
from ..db.models import Token, Wallet, TokenSnapshot

class DataSync:
    def __init__(self, db: Session, dune: DuneClient, solana: SolanaRPC):
        self.db = db
        self.dune = dune
        self.solana = solana
    
    async def sync_recent_tokens(self, hours: int = 24) -> List[Dict]:
        """Sync recently launched tokens from Dune to our database"""
        tokens = await self.dune.query("token_analysis/launches", params={"hours": hours})
        
        synced = []
        for token_data in tokens:
            # Check if token exists
            token = self.db.query(Token).filter(Token.address == token_data["token_address"]).first()
            
            if not token:
                token = Token(
                    address=token_data["token_address"],
                    name=token_data.get("token_name"),
                    symbol=token_data.get("token_symbol"),
                    decimals=token_data.get("decimals", 9),
                    launch_time=token_data.get("launch_time"),
                    deployer=token_data.get("deployer_address")
                )
                self.db.add(token)
                synced.append({"action": "created", "token": token.address})
            else:
                synced.append({"action": "exists", "token": token.address})
        
        self.db.commit()
        return synced
    
    async def take_token_snapshots(self) -> List[Dict]:
        """Take periodic snapshots of token metrics"""
        tokens = self.db.query(Token).filter(Token.is_active == True).all()
        
        snapshots = []
        for token in tokens:
            # Get current data
            liquidity = await self.dune.query("token_analysis/liquidity", 
                                           params={"token_address": token.address})
            holders = await self.dune.query("token_analysis/supply_distribution",
                                         params={"token_address": token.address})
            
            if liquidity and holders:
                snapshot = TokenSnapshot(
                    token_address=token.address,
                    liquidity_usd=liquidity[0].get("current_liquidity", 0),
                    top_holder_pct=holders[0].get("top_holder_pct", 100),
                    unique_holders=holders[0].get("unique_holders", 1),
                    timestamp=datetime.utcnow()
                )
                self.db.add(snapshot)
                snapshots.append({"token": token.address, "snapshot_id": snapshot.id})
        
        self.db.commit()
        return snapshots