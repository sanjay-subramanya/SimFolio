import yfinance as yf
import pandas as pd

def get_historical_snapshot(user_stocks, date, days_back=30):
    """Get historical data for backtesting"""
    end_date = pd.Timestamp(date)
    start_date = end_date - pd.Timedelta(days=days_back + 30)
    
    data = yf.download(user_stocks, start=start_date, end=end_date, interval='1d', progress=False, auto_adjust=True)
    prices = data['Close'].dropna()
    
    returns = prices.pct_change()
    actual_moves = returns.iloc[-days_back:]
    
    return {
        'prices': prices.iloc[-days_back:],
        'actual_moves': actual_moves,
        'date': end_date
    }