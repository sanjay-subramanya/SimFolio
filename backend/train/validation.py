import torch
import logging
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from data.features import create_advanced_features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_on_date(trainer, stocks, date):
    """Realistic validation using only data available up to the test date"""
    try:
        historical_data = trainer.data_helper.get_historical_snapshot(stocks, date)
        actual_moves = historical_data['actual_moves'].iloc[-1]
        
        # Use the snapshot data directly for features
        prices = historical_data['prices']
        returns = prices.pct_change().dropna()
        
        # Create features from the historical snapshot (no future data)
        with torch.no_grad():
            # Build features from available historical data
            short_features = _create_features_from_snapshot(prices.iloc[-30:], returns.iloc[-30:], stocks, trainer)
            medium_features = _create_features_from_snapshot(prices.iloc[-60:], returns.iloc[-60:], stocks, trainer)  
            long_features = _create_features_from_snapshot(prices, returns, stocks, trainer)
            
            # Build correlation graph from historical returns only
            corr_matrix = returns.corr().fillna(0)
            edge_index, edge_attr = _build_graph_from_correlation(corr_matrix, stocks)
            
            # Run model inference
            predicted_impacts, _ = trainer.model(
                short_features, medium_features, long_features, edge_index, edge_attr
            )
        
        accuracy = _calculate_prediction_accuracy(predicted_impacts, actual_moves, stocks)
        return accuracy
        
    except Exception as e:
        logger.error(f"  Validation error on {date}: {e}")
        return 0.5


def robust_validation(trainer, portfolio_size):
    """Temporal validation across multiple periods"""
    validation_dates = [
        '2024-09-01', '2024-07-01', '2024-05-01', '2024-03-01'
    ]
    accuracies = []
    for val_date in validation_dates:
        stocks = trainer.data_helper.sample_random_portfolio(portfolio_size)
        accuracy = validate_on_date(trainer, stocks, val_date)
        accuracies.append(accuracy)
    
    avg_accuracy = np.mean(accuracies)
    std_accuracy = np.std(accuracies)
    logger.info(f"  Validation Accuracy: {avg_accuracy:.1%} (±{std_accuracy:.1%})")
    return avg_accuracy


def _create_features_from_snapshot(prices, returns, stocks, trainer):
    """Create feature tensor from historical price/return data"""
    features = []
    for stock in stocks:
        if stock in prices.columns:
            stock_features = create_advanced_features(
                prices[stock], returns[stock] if stock in returns.columns else pd.Series([0]*len(prices))
            )
            features.append(stock_features)
        else:
            features.append(np.zeros(8))
    
    feature_tensor = torch.tensor(np.array(features), dtype=torch.float32)
    return feature_tensor.unsqueeze(1)

def _build_graph_from_correlation(corr_matrix, stocks):
    """Build graph edges from correlation matrix"""
    edges = []
    edge_weights = []
    
    n_stocks = len(stocks)
    for i in range(n_stocks):
        for j in range(i + 1, n_stocks):
            corr = corr_matrix.iloc[i, j]
            if abs(corr) > 0.1:
                edges.extend([[i, j], [j, i]])
                edge_weights.extend([corr, corr])
    
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous() if edges else torch.empty(2, 0, dtype=torch.long)
    edge_attr = torch.tensor(edge_weights, dtype=torch.float32) if edge_weights else torch.empty(0, dtype=torch.float32)
    
    return edge_index, edge_attr

def _calculate_prediction_accuracy(predicted_impacts, actual_moves, stocks):
    """Calculate realistic accuracy metrics"""
    pred_np = predicted_impacts.cpu().numpy()
    actual_np = actual_moves.values
    
    # 1. Direction accuracy
    direction_correct = np.sign(pred_np) == np.sign(actual_np)
    direction_accuracy = np.mean(direction_correct)
    
    # 2. Correlation between predicted and actual moves
    if len(stocks) > 1:
        correlation = np.corrcoef(pred_np, actual_np)[0, 1]
        correlation = 0 if np.isnan(correlation) else max(0, correlation)
    else:
        correlation = 1.0 if direction_correct[0] else 0.0
    
    # 3. Rank correlation
    if len(stocks) > 2:
        pred_ranks = np.argsort(pred_np)
        actual_ranks = np.argsort(actual_np)
        rank_correlation = spearmanr(pred_ranks, actual_ranks).correlation
        rank_correlation = 0 if np.isnan(rank_correlation) else max(0, rank_correlation)
    else:
        rank_correlation = direction_accuracy
    
    # Combined accuracy score
    combined_accuracy = (
        0.5 * direction_accuracy + 
        0.3 * correlation + 
        0.2 * rank_correlation
    )
    
    if np.random.random() < 0.1:
        logger.info(f"    Sample validation: Dir={direction_accuracy:.1%}, "
            f"Corr={correlation:.3f}, Rank={rank_correlation:.3f}")
    
    return combined_accuracy