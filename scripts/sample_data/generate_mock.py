import json
from faker import Faker
import random
from datetime import datetime, timedelta
from pathlib import Path

fake = Faker()

def generate_token_data(num_tokens=20):
    tokens = []
    for _ in range(num_tokens):
        launch_time = fake.date_time_this_month()
        tokens.append({
            "token_address": fake.sha256()[:44],
            "token_name": fake.cryptocurrency_name(),
            "token_symbol": fake.cryptocurrency_code(),
            "launch_time": launch_time.isoformat(),
            "deployer": fake.sha256()[:44],
            "initial_liquidity": random.randint(1000, 100000),
            "current_liquidity": random.randint(0, 100000)
        })
    return tokens

def generate_wallet_data(num_wallets=15):
    wallets = []
    for _ in range(num_wallets):
        wallets.append({
            "wallet_address": fake.sha256()[:44],
            "first_seen": fake.date_time_this_year().isoformat(),
            "last_active": fake.date_time_this_month().isoformat(),
            "tokens_held": random.randint(1, 20),
            "risk_score": round(random.uniform(0, 1), 2)
        })
    return wallets

def save_sample_data():
    data_dir = Path("sample_data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate and save data
    with open(data_dir / "tokens.json", "w") as f:
        json.dump(generate_token_data(), f, indent=2)
    
    with open(data_dir / "wallets.json", "w") as f:
        json.dump(generate_wallet_data(), f, indent=2)
    
    print(f"Sample data generated in {data_dir}")

if __name__ == "__main__":
    save_sample_data()