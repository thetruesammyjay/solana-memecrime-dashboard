from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from ..utils.dune_client import DuneClient
from ..utils.solana_rpc import SolanaRPC
from ...services.risk_scoring import calculate_token_risk
from ...db.models import TokenAlert

router = APIRouter(prefix="/tokens", tags=["tokens"])

@router.get("/{token_address}")
async def get_token_details(
    token_address: str,
    dune: DuneClient = Depends(),
    solana: SolanaRPC = Depends()
):
    """Get comprehensive token details including risk analysis"""
    # Get on-chain data
    token_data = await dune.query("token_analysis/launches", params={"token_address": token_address})
    liquidity_data = await dune.query("token_analysis/liquidity", params={"token_address": token_address})
    holders_data = await dune.query("token_analysis/supply_distribution", params={"token_address": token_address})
    
    # Get real-time price data
    price_data = await solana.get_token_price(token_address)
    
    # Calculate risk score
    risk_data = calculate_token_risk({
        **token_data[0],
        **liquidity_data[0],
        **holders_data[0],
        **price_data
    })
    
    return {
        "token": token_data[0],
        "liquidity": liquidity_data,
        "holders": holders_data,
        "price": price_data,
        "risk": risk_data
    }

@router.get("/{token_address}/transactions")
async def get_token_transactions(
    token_address: str,
    timeframe: Optional[int] = 24,
    limit: Optional[int] = 100,
    solana: SolanaRPC = Depends()
):
    """Get recent transactions for a token"""
    return await solana.get_token_transactions(token_address, hours=timeframe, limit=limit)

@router.post("/{token_address}/watch")
async def watch_token(
    token_address: str,
    alert_threshold: float,
    alert_type: str = "risk_score",
    db: Session = Depends(get_db)
):
    """Create a watch alert for a token"""
    alert = TokenAlert(
        token_address=token_address,
        alert_type=alert_type,
        threshold=alert_threshold,
        created_at=datetime.utcnow(),
        is_active=True
    )
    db.add(alert)
    db.commit()
    return {"status": "watching", "alert_id": alert.id}