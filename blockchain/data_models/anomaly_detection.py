import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from typing import Tuple, Dict
import warnings

class AnomalyDetector:
    def __init__(self, min_samples: int = 10):
        self.min_samples = min_samples
        self.models = {
            'volume': IsolationForest(contamination=0.1),
            'price': IsolationForest(contamination=0.05)
        }
    
    def detect_volume_anomalies(self, volume_series: pd.Series) -> Tuple[pd.Series, Dict]:
        """Detect abnormal trading volume patterns"""
        if len(volume_series) < self.min_samples:
            warnings.warn(f"Insufficient samples ({len(volume_series)} < {self.min_samples})")
            return pd.Series(), {}
        
        # Z-score analysis
        log_vol = np.log1p(volume_series)
        z_scores = np.abs(stats.zscore(log_vol))
        z_threshold = 3
        
        # Machine learning approach
        X = log_vol.values.reshape(-1, 1)
        self.models['volume'].fit(X)
        ml_scores = self.models['volume'].decision_function(X)
        
        # Combined results
        anomalies = (z_scores > z_threshold) | (ml_scores < -0.2)
        stats = {
            'z_score_threshold': z_threshold,
            'max_z_score': max(z_scores),
            'mean_volume': volume_series.mean(),
            'std_volume': volume_series.std(),
            'anomaly_count': sum(anomalies)
        }
        
        return anomalies, stats
    
    def detect_price_anomalies(self, price_series: pd.Series) -> Tuple[pd.Series, Dict]:
        """Identify abnormal price movements"""
        if len(price_series) < self.min_samples:
            warnings.warn(f"Insufficient samples ({len(price_series)} < {self.min_samples})")
            return pd.Series(), {}
        
        returns = price_series.pct_change().dropna()
        log_returns = np.log1p(returns)
        
        # Bayesian changepoint detection
        mean_before = log_returns.expanding().mean()
        std_before = log_returns.expanding().std()
        bayes_scores = np.abs((log_returns - mean_before) / std_before)
        
        # Machine learning approach
        X = log_returns.values.reshape(-1, 1)
        self.models['price'].fit(X)
        ml_scores = self.models['price'].decision_function(X)
        
        # Combined results
        anomalies = (bayes_scores > 3) | (ml_scores < -0.15)
        stats = {
            'max_return': returns.max(),
            'min_return': returns.min(),
            'volatility': returns.std(),
            'anomaly_count': sum(anomalies)
        }
        
        return anomalies, stats
    
    def detect_wash_trading(self, 
                          price_series: pd.Series, 
                          volume_series: pd.Series,
                          buy_ratio: pd.Series) -> Dict:
        """Identify potential wash trading patterns"""
        corr = price_series.corr(volume_series)
        buy_ratio_std = buy_ratio.std()
        
        return {
            'price_volume_correlation': corr,
            'buy_ratio_volatility': buy_ratio_std,
            'wash_score': (1 - abs(corr)) * buy_ratio_std  # 0-1 scale
        }