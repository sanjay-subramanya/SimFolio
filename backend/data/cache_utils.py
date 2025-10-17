import os
import pickle
from datetime import datetime, timedelta

def get_cache_key(stocks, period, interval):
    """Generate unique cache key"""
    stocks_key = "_".join(sorted(stocks))
    return f"{stocks_key}_{period}_{interval}.pkl"

def is_cache_valid(cache_file, cache_expiry_days):
    """Check if cache is still fresh"""
    if not os.path.exists(cache_file):
        return False
    file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    return (datetime.now() - file_time) < timedelta(days=cache_expiry_days)

def save_to_cache(data, cache_key, cache_dir):
    """Save data to cache file"""
    cache_file = os.path.join(cache_dir, cache_key)
    with open(cache_file, 'wb') as f:
        pickle.dump({'data': data, 'timestamp': datetime.now()}, f)

def load_from_cache(cache_key, cache_dir):
    """Load data from cache"""
    cache_file = os.path.join(cache_dir, cache_key)
    with open(cache_file, 'rb') as f:
        cached = pickle.load(f)
    return cached['data']

def clear_cache():
        """Clear all cached data"""
        import os
        import glob
        files = glob.glob(f"{self.cache_dir}/*.pkl")
        for file in files:
            os.remove(file)