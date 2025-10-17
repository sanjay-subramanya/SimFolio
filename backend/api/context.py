import torch
from pathlib import Path
from data.core import StockData
from train.models import TemporalGNN
from config.settings import Config

class AppContext:
    def __init__(self):
        self.model_path = str(Config.model_dir / "temporal_gnn_2.pt")
        self.stock_data = StockData()
        self.all_stocks = self.stock_data.stock_universe
        self.model = self._load_model(self.model_path)

    def _load_model(self, model_path):
        try:
            model = TemporalGNN()
            checkpoint = torch.load(model_path, map_location='cpu')
            model.load_state_dict(checkpoint)
            model.eval()
            return model
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {model_path}: {e}")
