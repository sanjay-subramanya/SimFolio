import torch
import torch.nn.functional as F

def curriculum_loss(trainer, impacts, data, stocks=None):
    n_stocks = len(stocks)
    
    # Get actual next-day returns
    latest_returns = data['timeframes']['short']['returns'].iloc[-1]
    targets = torch.tensor([latest_returns[stock] for stock in stocks], dtype=torch.float32)
    
    loss = F.mse_loss(impacts, targets)
    return loss