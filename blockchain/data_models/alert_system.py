import requests
from datetime import datetime, timedelta
from typing import List, Dict

class RugPullAlert:
    def __init__(self, webhook_url: str, min_score: int = 70):
        self.webhook = webhook_url
        self.min_score = min_score
        self.last_alert_time = datetime.utcnow() - timedelta(hours=1)

    def generate_alert(self, token: Dict) -> Dict:
        """Create standardized alert message"""
        return {
            "token": token['symbol'],
            "address": token['token_address'],
            "score": token['rug_pull_score'],
            "risk": token['risk_category'],
            "indicators": {
                "holder_concentration": token['holder_concentration'],
                "price_swing": token['price_swing'],
                "deployer_history": token['creator_previous_tokens']
            },
            "links": {
                "solscan": token['explorer_link'],
                "dexscreener": token['dexscreener_link']
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    def send_alerts(self, risky_tokens: List[Dict]):
        """Send alerts for high-risk tokens"""
        new_alerts = [
            self.generate_alert(t) 
            for t in risky_tokens 
            if t['rug_pull_score'] >= self.min_score
        ]
        
        if new_alerts:
            payload = {
                "text": "🚨 Solana Rug Pull Alerts",
                "attachments": [{
                    "color": "#ff0000",
                    "fields": [
                        {"title": "Token", "value": f"{a['token']} ({a['address']})", "short": True},
                        {"title": "Risk Score", "value": a['score'], "short": True},
                        {"title": "Key Indicators", "value": f"""
                        • Holder Concentration: {a['indicators']['holder_concentration']:.2%}
                        • Price Swing: {a['indicators']['price_swing']:.2f}x
                        • Deployer Tokens: {a['indicators']['deployer_history']}
                        """}
                    ],
                    "actions": [
                        {"type": "button", "text": "View on Solscan", "url": a['links']['solscan']},
                        {"type": "button", "text": "DexScreener", "url": a['links']['dexscreener']}
                    ]
                } for a in new_alerts]
            }
            
            try:
                requests.post(self.webhook, json=payload)
                self.last_alert_time = datetime.utcnow()
                return True
            except Exception as e:
                print(f"Alert failed: {str(e)}")
                return False
        return False

# Example usage
if __name__ == "__main__":
    alert = RugPullAlert(webhook_url="YOUR_SLACK_WEBHOOK")
    
    # Mock data from your SQL query
    test_tokens = [{
        'token_address': 'TEST123',
        'symbol': 'TEST',
        'rug_pull_score': 85,
        'risk_category': 'HIGH_RISK',
        'holder_concentration': 0.95,
        'price_swing': 6.2,
        'creator_previous_tokens': 4,
        'explorer_link': 'https://solscan.io/token/TEST123',
        'dexscreener_link': 'https://dexscreener.com/solana/TEST123'
    }]
    
    alert.send_alerts(test_tokens)