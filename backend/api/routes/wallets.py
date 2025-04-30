from fastapi import APIRouter, Depends
from typing import Optional
from ..utils.dune_client import DuneClient
from ..utils.solana_rpc import SolanaRPC
from ...services.risk_scoring import calculate_wallet_risk
from ...db.models import Wallet, WalletAlert

router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.get("/{wallet_address}")
async def get_wallet_details(
    wallet_address: str,
    dune: DuneClient = Depends(),
    solana: SolanaRPC = Depends()
):
    """Get wallet activity and associated risk profile"""
    # Get wallet cluster data
    cluster_data = await dune.query("wallet_analysis/clustering", params={"wallet_address": wallet_address})
    
    # Get deployer history if exists
    deployer_data = await dune.query("wallet_analysis/deployers", params={"wallet_address": wallet_address})
    
    # Get recent transactions
    txs = await solana.get_wallet_transactions(wallet_address)
    
    # Calculate risk score
    risk_data = calculate_wallet_risk({
        "cluster": cluster_data[0] if cluster_data else None,
        "deployer": deployer_data[0] if deployer_data else None,
        "tx_count": len(txs),
        "last_active": txs[0]["block_time"] if txs else None
    })
    
    return {
        "wallet": wallet_address,
        "cluster": cluster_data,
        "deployer": deployer_data,
        "recent_txs": txs[:10],
        "risk": risk_data
    }

@router.get("/{wallet_address}/tokens")
async def get_wallet_tokens(
    wallet_address: str,
    solana: SolanaRPC = Depends()
):
    """Get all tokens held by a wallet"""
    return await solana.get_wallet_tokens(wallet_address)

@router.post("/{wallet_address}/watch")
async def watch_wallet(
    wallet_address: str,
    alert_type: str = "new_token_deploy",
    db: Session = Depends(get_db)
):
    """Create a watch alert for a wallet"""
    alert = WalletAlert(
        wallet_address=wallet_address,
        alert_type=alert_type,
        created_at=datetime.utcnow(),
        is_active=True
    )
    db.add(alert)
    db.commit()
    return {"status": "watching", "alert_id": alert.id}