import os
from pathlib import Path

class Config:
    # General settings
    parent_dir = Path(__file__).resolve().parent.parent
    model_dir = parent_dir / "saved_models"
    cache_dir = parent_dir / "data/stock_cache"

    # Training settings
    feature_dim = 8
    hidden_dim = 64
    temporal_dim = 128
    gnn_dim = 128

    train_curriculum = [
            {'size': 4, 'epochs': 20, 'name': 'Small Portfolios'},
            {'size': 8, 'epochs': 20, 'name': 'Medium Portfolios'}, 
            {'size': 12, 'epochs': 20, 'name': 'Large Portfolios'}]
    
    # Phase-specific learning rates
    learning_rates = [0.007, 0.003, 0.0005]
