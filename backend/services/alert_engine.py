import asyncio
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..db.models import TokenAlert, WalletAlert, AlertHistory
from ..utils.dune_client import DuneClient
from ..utils.solana_rpc import SolanaRPC
from .risk_scoring import RiskScorer

class AlertEngine:
    def __init__(self, db: Session, dune: DuneClient, solana: SolanaRPC):
        self.db = db
        self.dune = dune
        self.solana = solana
        self.scorer = RiskScorer()
    
    async def check_all_alerts(self) -> List[Dict]:
        """Check all active alerts and trigger notifications"""
        triggered_alerts = []
        
        # Check token alerts
        token_alerts = self.db.query(TokenAlert).filter(TokenAlert.is_active == True).all()
        for alert in token_alerts:
            triggered = await self._check_token_alert(alert)
            if triggered:
                triggered_alerts.append(triggered)
        
        # Check wallet alerts
        wallet_alerts = self.db.query(WalletAlert).filter(WalletAlert.is_active == True).all()
        for alert in wallet_alerts:
            triggered = await self._check_wallet_alert(alert)
            if triggered:
                triggered_alerts.append(triggered)
        
        return triggered_alerts
    
    async def _check_token_alert(self, alert: TokenAlert) -> Optional[Dict]:
        """Check if a token alert condition is met"""
        token_data = await self.dune.query("token_analysis/launches", params={"token_address": alert.token_address})
        if not token_data:
            return None
        
        risk_data = self.scorer.calculate_token_risk(token_data[0])
        
        # Check if threshold is crossed
        if risk_data["score"] <= alert.threshold:
            # Record alert history
            history = AlertHistory(
                alert_id=alert.id,
                alert_type="token",
                triggered_value=risk_data["score"],
                triggered_at=datetime.utcnow()
            )
            self.db.add(history)
            self.db.commit()
            
            return {
                "alert_id": alert.id,
                "token_address": alert.token_address,
                "triggered_value": risk_data["score"],
                "risk_data": risk_data
            }
        return None
    
    async def _check_wallet_alert(self, alert: WalletAlert) -> Optional[Dict]:
        """Check if a wallet alert condition is met"""
        if alert.alert_type == "new_token_deploy":
            # Check for new token deployments
            deploy_data = await self.dune.query("wallet_analysis/deployers", 
                                              params={"wallet_address": alert.wallet_address})
            
            if deploy_data and deploy_data[0]["last_deploy"] > alert.created_at:
                # Record alert history
                history = AlertHistory(
                    alert_id=alert.id,
                    alert_type="wallet",
                    triggered_value=1,
                    triggered_at=datetime.utcnow()
                )
                self.db.add(history)
                self.db.commit()
                
                return {
                    "alert_id": alert.id,
                    "wallet_address": alert.wallet_address,
                    "triggered_value": 1,
                    "deploy_data": deploy_data[0]
                }
        return None