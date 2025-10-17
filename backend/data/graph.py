import torch
import logging
import yfinance as yf
from torch_geometric.data import Data
from data.features import process_timeframe_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_correlation_graph(user_stocks, returns_data):
    """Build graph from correlation matrix"""
    corr_matrix = returns_data.corr().fillna(0)
    
    edges = []
    edge_weights = []
    
    for i in range(len(user_stocks)):
        for j in range(i + 1, len(user_stocks)):
            corr = corr_matrix.iloc[i, j]
            if abs(corr) > 0.2:
                edges.extend([[i, j], [j, i]])
                edge_weights.extend([corr, corr])

    # Fallback connectivity
    if len(edges) == 0:
        logger.info(f"  ⚠️  No strong correlations found. Creating minimum graph connectivity.")
        for i in range(len(user_stocks)):
            correlations = corr_matrix.iloc[i].abs()
            correlations.iloc[i] = 0
            if len(correlations) > 1:
                j = correlations.idxmax()
                j_idx = user_stocks.index(j)
                corr = corr_matrix.iloc[i, j_idx]
                edges.extend([[i, j_idx], [j_idx, i]])
                edge_weights.extend([corr, corr])
    
    if len(edges) == 0 and len(user_stocks) > 1:
        logger.info(f"  ⚠️  Creating chain connectivity fallback.")
        for i in range(len(user_stocks) - 1):
            edges.extend([[i, i+1], [i+1, i]])
            edge_weights.extend([0.1, 0.1])
    
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous() if edges else torch.empty(2, 0, dtype=torch.long)
    edge_attr = torch.tensor(edge_weights, dtype=torch.float32) if edge_weights else torch.empty(0, dtype=torch.float32)
    
    # Create node features from short-term data
    short_data = yf.download(user_stocks, period='1mo', interval='1d', progress=False, auto_adjust=True)
    short_features = process_timeframe_data(short_data, user_stocks, 30)['features']
    
    graph_data = Data(x=short_features, edge_index=edge_index, edge_attr=edge_attr)
    
    return graph_data, corr_matrix