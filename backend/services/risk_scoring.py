from typing import Dict
import numpy as np
from sklearn.ensemble import IsolationForest

class RiskScorer:
    def __init__(self):
        # Initialize models
        self.token_model = IsolationForest(n_estimators=100, contamination=0.1)
        self.wallet_model = IsolationForest(n_estimators=100, contamination=0.1)
        
        # Initialize thresholds
        self.token_thresholds = {
            "liquidity_removal": 0.7,
            "holder_concentration": 0.8,
            "price_drop": 0.9,
            "volume_spike": 10.0
        }
    
    def calculate_token_risk(self, token_data: Dict) -> Dict:
        """Calculate comprehensive risk score for a token"""
        # Extract features
        features = np.array([[
            token_data.get("liquidity_removed_pct", 0),
            token_data.get("top_holder_pct", 0),
            token_data.get("mcap_drop_pct", 0),
            token_data.get("volume_change_24h", 1)
        ]])
        
        # Calculate anomaly score
        risk_score = self.token_model.decision_function(features)[0]
        is_anomaly = self.token_model.predict(features)[0] == -1
        
        # Rule-based checks
        rule_checks = {
            "high_liquidity_removal": token_data.get("liquidity_removed_pct", 0) > self.token_thresholds["liquidity_removal"],
            "high_holder_concentration": token_data.get("top_holder_pct", 0) > self.token_thresholds["holder_concentration"],
            "large_price_drop": token_data.get("mcap_drop_pct", 0) > self.token_thresholds["price_drop"],
            "suspicious_volume": token_data.get("volume_change_24h", 1) > self.token_thresholds["volume_spike"]
        }
        
        # Composite risk level
        triggered_rules = sum(rule_checks.values())
        if triggered_rules >= 3 or is_anomaly:
            risk_level = "critical"
        elif triggered_rules >= 2:
            risk_level = "high"
        elif triggered_rules >= 1:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "score": float(risk_score),
            "level": risk_level,
            "is_anomaly": bool(is_anomaly),
            "triggered_rules": rule_checks
        }
    
    def calculate_wallet_risk(self, wallet_data: Dict) -> Dict:
        """Calculate risk score for a wallet"""
        # Extract features
        features = np.array([[
            len(wallet_data.get("deployer", {}).get("deployed_tokens", [])),
            wallet_data.get("deployer", {}).get("total_sells_usd", 0),
            wallet_data.get("cluster", {}).get("cluster_size", 1),
            wallet_data.get("tx_count", 0)
        ]])
        
        # Calculate anomaly score
        risk_score = self.wallet_model.decision_function(features)[0]
        is_anomaly = self.wallet_model.predict(features)[0] == -1
        
        # Risk level based on score
        if risk_score < -0.5 or is_anomaly:
            risk_level = "high"
        elif risk_score < 0:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "score": float(risk_score),
            "level": risk_level,
            "is_anomaly": bool(is_anomaly)
        }