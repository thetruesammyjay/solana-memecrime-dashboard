import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.models import Token, Wallet

def load_sample_data(db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Load tokens
    with open('sample_data/tokens.json') as f:
        tokens = json.load(f)
        for token in tokens:
            session.add(Token(**token))
    
    # Load wallets
    with open('sample_data/wallets.json') as f:
        wallets = json.load(f)
        for wallet in wallets:
            session.add(Wallet(**wallet))
    
    session.commit()
    print(f"Loaded {len(tokens)} tokens and {len(wallets)} wallets")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    load_sample_data(os.getenv("DATABASE_URL"))