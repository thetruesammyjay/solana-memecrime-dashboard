from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(44), unique=True, nullable=False)
    name = Column(String(100))
    symbol = Column(String(10))
    decimals = Column(Integer, default=9)
    launch_time = Column(DateTime)
    deployer = Column(String(44))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    snapshots = relationship("TokenSnapshot", back_populates="token")
    alerts = relationship("TokenAlert", back_populates="token")

class Wallet(Base):
    __tablename__ = 'wallets'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(44), unique=True, nullable=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    risk_score = Column(Float)
    
    alerts = relationship("WalletAlert", back_populates="wallet")

class TokenSnapshot(Base):
    __tablename__ = 'token_snapshots'
    
    id = Column(Integer, primary_key=True)
    token_address = Column(String(44), ForeignKey('tokens.address'))
    liquidity_usd = Column(Float)
    top_holder_pct = Column(Float)
    unique_holders = Column(Integer)
    price_usd = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    token = relationship("Token", back_populates="snapshots")

class TokenAlert(Base):
    __tablename__ = 'token_alerts'
    
    id = Column(Integer, primary_key=True)
    token_address = Column(String(44), ForeignKey('tokens.address'))
    alert_type = Column(String(50))
    threshold = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    resolved_at = Column(DateTime)
    
    token = relationship("Token", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="token_alert")

class WalletAlert(Base):
    __tablename__ = 'wallet_alerts'
    
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String(44), ForeignKey('wallets.address'))
    alert_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    resolved_at = Column(DateTime)
    
    wallet = relationship("Wallet", back_populates="alerts")
    history = relationship("AlertHistory", back_populates="wallet_alert")

class AlertHistory(Base):
    __tablename__ = 'alert_history'
    
    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer)
    alert_type = Column(String(20))  # 'token' or 'wallet'
    triggered_value = Column(Float)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships for both types of alerts
    token_alert_id = Column(Integer, ForeignKey('token_alerts.id'))
    wallet_alert_id = Column(Integer, ForeignKey('wallet_alerts.id'))
    
    token_alert = relationship("TokenAlert", back_populates="history")
    wallet_alert = relationship("WalletAlert", back_populates="history")