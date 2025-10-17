import os
import logging
import torch
import yfinance as yf
import pandas as pd
import numpy as np
from torch_geometric.data import Data
from config.settings import Config
from data.stocks import TICKERS
from data.cache_utils import get_cache_key, is_cache_valid, save_to_cache, load_from_cache
from data.features import process_timeframe_data
from data.historical import get_historical_snapshot
from data.graph import build_correlation_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockData:
    def __init__(self, cache_dir=str(Config.cache_dir), cache_expiry_days=7):
        self.stock_universe = TICKERS
        self.cache_expiry_days = cache_expiry_days
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def download_all_data_once(self):
        """ONE-TIME: Download each stock individually"""
        logger.info("Downloading all stocks individually...")

        
        timeframes = {
            'short': ('1mo', '1d'),
            'medium': ('3mo', '1wk'),
            'long': ('6mo', '1wk')
        }
        
        for stock in self.stock_universe:
            for timeframe, (period, interval) in timeframes.items():
                cache_key = get_cache_key([stock], period, interval)
                cache_file = f"{self.cache_dir}/{cache_key}"
                
                if not is_cache_valid(cache_file, self.cache_expiry_days):
                    logger.info(f"Downloading {stock} ({timeframe})...")
                    try:
                        data = yf.download([stock], period=period, interval=interval,
                                        progress=False, auto_adjust=True)
                        save_to_cache(data, cache_key, self.cache_dir)
                    except Exception as e:
                        logger.error(f"Failed {stock}: {e}")
        
        logger.info("All stocks downloaded individually!")
    
    def get_multi_timeframe_data(self, user_stocks):
        """Inference: Combine pre-downloaded individual stock data"""
        timeframe_data = {}
        
        for timeframe, config in {
            'short': ('1mo', '1d', 30),
            'medium': ('3mo', '1wk', 12), 
            'long': ('6mo', '1wk', 24)
        }.items():
            period, interval, seq_len = config
            
            # Combine individual stock data
            combined_data = None
            for stock in user_stocks:
                cache_key = get_cache_key([stock], period, interval)
                cache_file = f"{self.cache_dir}/{cache_key}"
                
                if not is_cache_valid(cache_file, self.cache_expiry_days):
                    raise Exception(f"Data missing for {stock}. Run download_all_data_once() first!")
                
                stock_data = load_from_cache(cache_key, self.cache_dir)
                
                if combined_data is None:
                    combined_data = stock_data
                else:
                    combined_data = pd.concat([combined_data, stock_data], axis=1)
            
            timeframe_data[timeframe] = process_timeframe_data(combined_data, user_stocks, seq_len)
        
        graph_data, corr_matrix = build_correlation_graph(user_stocks, timeframe_data['short']['returns'])
        
        return {
            'timeframes': timeframe_data,
            'stocks': user_stocks,
            'correlations': corr_matrix,
            'graph': graph_data
        }
    
    def get_historical_snapshot(self, user_stocks, date, days_back=30):
        return get_historical_snapshot(user_stocks, date, days_back)

    def sample_random_portfolio(self, size):
        """Sample random stocks from universe"""
        return np.random.choice(self.stock_universe, size=size, replace=False).tolist()
    
    