import torch
import logging
import torch.nn.functional as F
import numpy as np
import pandas as pd
from data.core import StockData
from train.models import TemporalGNN
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurriculumTrainer:
    def __init__(self):
        self.data_helper = StockData()
        self.all_stocks = self.data_helper.stock_universe
        self.model = TemporalGNN()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001, weight_decay=1e-4)
        self.performance_history = []
    
    def curriculum_learning(self):
        """Curriculum learning with dynamic portfolios"""
        curriculum = Config.train_curriculum
        
        for phase, config in enumerate(curriculum):
            logger.info(f"\nCurriculum Phase {phase + 1}: {config['name']}")
            self.train_phase(config['size'], config['epochs'], phase)
            
            # Validate after each phase
            val_accuracy = self.robust_validation(config['size'])
            self.performance_history.append({
                'phase': phase + 1,
                'portfolio_size': config['size'],
                'accuracy': val_accuracy
            })
    
    def train_phase(self, portfolio_size, epochs, phase):
        """Train on random portfolios of specific size"""
        learning_rate = Config.learning_rates[phase] if phase < len(Config.learning_rates) else 0.0001
        
        # Update optimizer for this phase
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = learning_rate
        
        for epoch in range(1, 1 + epochs):
            # New random portfolio each epoch
            stocks = self.data_helper.sample_random_portfolio(portfolio_size)
            data = self.data_helper.get_multi_timeframe_data(stocks)
            
            self.model.train()
            self.optimizer.zero_grad()
            
            # Get features with proper shape handling
            short_features = data['timeframes']['short']['features']
            medium_features = data['timeframes']['medium']['features']
            long_features = data['timeframes']['long']['features']
            
            # Add sequence dimension if needed (for GRU)
            if short_features.dim() == 2:
                short_features = short_features.unsqueeze(1)
                medium_features = medium_features.unsqueeze(1)
                long_features = long_features.unsqueeze(1)
            
            impacts, uncertainties = self.model(
                short_features,
                medium_features, 
                long_features,
                data['graph'].edge_index,
                data['graph'].edge_attr
            )
  
            loss = self.curriculum_loss(impacts, data, stocks)
            loss.backward()

            grad_norm = 0
            for param in self.model.parameters():
                if param.grad is not None:
                    grad_norm += param.grad.norm().item()
                    
            # if epoch % 10 == 0:
            #     logger.info(f"  Grad Norm: {grad_norm:.4f}")
            
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()
            
            # Diagnostics
            if epoch % 10 == 0:
                impact_range = (impacts.max() - impacts.min()).item()
                impact_std = impacts.std().item()

                logger.info("""\nEpoch %d: \n- Grad Norm: %.4f \n- Loss: %.4f \n- Impacts - Range: %.4f, Std: %.4f""", 
                epoch, grad_norm, loss.item(), impact_range, impact_std)

    