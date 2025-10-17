import logging
import numpy as np
import pandas as pd
from train.validation import validate_on_date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def historical_backtesting(trainer, portfolio_size=15, days=20):
    """Realistic backtesting with proper temporal validation"""
    logger.info(f"  Portfolios: {portfolio_size} stocks, {days} trading days")
    
    # Test on multiple random portfolios over time
    all_accuracies = []
    portfolio_results = []
    
    for portfolio_num in range(5):
        stocks = trainer.data_helper.sample_random_portfolio(portfolio_size)
        portfolio_accuracies = []
        
        logger.info(f"  Portfolio {portfolio_num+1}: {stocks[:3]}...")
        
        # Test this portfolio across multiple historical dates
        test_dates = pd.date_range(
            end=pd.Timestamp.now() - pd.Timedelta(days=7),
            periods=min(days, 30),
            freq='D'
        )
        
        for test_date in test_dates[-days:]:
            if test_date.weekday() < 5:
                accuracy = validate_on_date(trainer, stocks, test_date)
                portfolio_accuracies.append(accuracy)
        
        if portfolio_accuracies:
            portfolio_avg = np.mean(portfolio_accuracies)
            portfolio_std = np.std(portfolio_accuracies)
            all_accuracies.extend(portfolio_accuracies)
            
            portfolio_results.append({
                'stocks': stocks,
                'accuracy': portfolio_avg,
                'stability': 1 - portfolio_std
            })
            
            logger.info(f"    Accuracy: {portfolio_avg:.1%} ± {portfolio_std:.1%}")
    
    # Overall results
    if all_accuracies:
        overall_accuracy = np.mean(all_accuracies)
        overall_stability = 1 - np.std(all_accuracies)
        
        best_portfolio = max(portfolio_results, key=lambda x: x['accuracy'])
        worst_portfolio = min(portfolio_results, key=lambda x: x['accuracy'])
        
        logger.info(f"\nOVERALL BACKTESTING RESULTS:")
        logger.info(f"  Average Accuracy: {overall_accuracy:.1%}")
        logger.info(f"  Prediction Stability: {overall_stability:.1%}")
        logger.info(f"  Best Portfolio: {best_portfolio['stocks'][:3]}... ({best_portfolio['accuracy']:.1%})")
        logger.info(f"  Worst Portfolio: {worst_portfolio['stocks'][:3]}... ({worst_portfolio['accuracy']:.1%})")
        
        return overall_accuracy
    
    return 0.0