import numpy as np
import pandas as pd
import torch

def process_timeframe_data(data, user_stocks, seq_len):
    prices = data['Close'].dropna().iloc[-seq_len:]
    returns = prices.pct_change().dropna()
    
    feature_sequences = []
    for stock in user_stocks:
        if stock in prices.columns:
            stock_features = []
            for t in range(len(prices)):
                window_prices = prices[stock].iloc[max(0, t-20):t+1]
                window_returns = returns[stock].iloc[max(0, t-19):t+1] if t > 0 else pd.Series([0])
                features = create_advanced_features(window_prices, window_returns)
                stock_features.append(features)
            feature_sequences.append(np.array(stock_features))
        else:
            feature_sequences.append(np.zeros((len(prices), 8)))
    
    feature_tensor = torch.tensor(np.array(feature_sequences), dtype=torch.float32)
    
    return {
        'features': feature_tensor,
        'prices': prices,
        'returns': returns
    }

def create_advanced_features(prices, returns):
    """Create sophisticated financial features"""
    if len(prices) < 20:
        return np.zeros(8)
    
    # Price momentum features
    momentum_5 = (prices.iloc[-1] / prices.iloc[-6] - 1) if len(prices) >= 6 else 0
    momentum_10 = (prices.iloc[-1] / prices.iloc[-11] - 1) if len(prices) >= 11 else 0
    momentum_20 = (prices.iloc[-1] / prices.iloc[-21] - 1) if len(prices) >= 21 else 0
    
    # Volatility features
    vol_5 = returns.rolling(5).std().iloc[-1] if len(returns) >= 5 else 0
    vol_20 = returns.rolling(20).std().iloc[-1] if len(returns) >= 20 else 0
    
    # RSI
    rsi = _calculate_rsi(prices)
    
    # Bollinger Band position
    bb_position = _calculate_bollinger_position(prices)
    
    features = np.array([momentum_5, momentum_10, momentum_20, vol_5, vol_20, rsi, bb_position, returns.iloc[-1] if len(returns) > 0 else 0])
    
    return (features - features.mean()) / (features.std() + 1e-8)

def _calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return 50
    
    deltas = prices.diff()
    gains = deltas.where(deltas > 0, 0)
    losses = -deltas.where(deltas < 0, 0)
    
    avg_gain = gains.rolling(period).mean().iloc[-1]
    avg_loss = losses.rolling(period).mean().iloc[-1]
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def _calculate_bollinger_position(prices, period=20):
    """Calculate position within Bollinger Bands"""
    if len(prices) < period:
        return 0.5
    
    rolling_mean = prices.rolling(period).mean().iloc[-1]
    rolling_std = prices.rolling(period).std().iloc[-1]
    
    upper_band = rolling_mean + 2 * rolling_std
    lower_band = rolling_mean - 2 * rolling_std
    
    if upper_band - lower_band == 0:
        return 0.5
    
    return (prices.iloc[-1] - lower_band) / (upper_band - lower_band)