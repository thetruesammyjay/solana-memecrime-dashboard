import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    # Database
    DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/memecrime")
    
    # Dune Analytics
    DUNE_API_KEY = os.getenv("DUNE_API_KEY")
    
    # Solana
    SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    
    # Alerting
    ALERT_CHECK_INTERVAL = int(os.getenv("ALERT_CHECK_INTERVAL", 300))  # 5 minutes
    DATA_SYNC_INTERVAL = int(os.getenv("DATA_SYNC_INTERVAL", 3600))  # 1 hour
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    MIGRATIONS_DIR = BASE_DIR / "db" / "migrations"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "logs" / "app.log"
    
    @classmethod
    def validate(cls):
        """Validate required configurations"""
        if not cls.DUNE_API_KEY:
            raise ValueError("DUNE_API_KEY environment variable is required")
        
        if not cls.DB_URL:
            raise ValueError("DATABASE_URL environment variable is required")