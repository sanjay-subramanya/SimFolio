import torch
import logging
import torch.nn as nn
import pandas as pd
import numpy as np
from config.settings import Config
from train import CurriculumTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_and_validate():
    trainer = CurriculumTrainer()

    trainer.data_helper.download_all_data_once()
    
    logger.info(f"Training on {len(trainer.all_stocks)} total stocks")
    logger.info("Dynamic portfolio sampling each epoch")
    
    # Run curriculum learning
    trainer.curriculum_learning()
    
    # Save model
    model_path = str(Config.model_dir)/"temporal_gnn.pt"
    torch.save(trainer.model.state_dict(), model_path)
    logger.info(f"\nTraining completed! Model saved at {model_path}")
    
    # Backtest the trained model
    logger.info("Starting historical backtesting...")
    trainer.historical_backtesting(portfolio_size=np.random.randint(5, 12))
    logger.info("Historical backtesting completed!")

if __name__ == "__main__":
    train_and_validate()
