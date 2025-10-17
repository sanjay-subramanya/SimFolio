import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import softmax
from config.settings import Config

class TemporalEncoder(nn.Module):
    def __init__(self, feature_dim=Config.feature_dim, hidden_dim=Config.hidden_dim):
        super().__init__()
        
        # Encoders for different timeframes
        self.short_encoder = nn.GRU(feature_dim, hidden_dim, batch_first=True)
        self.medium_encoder = nn.GRU(feature_dim, hidden_dim, batch_first=True)
        self.long_encoder = nn.GRU(feature_dim, hidden_dim, batch_first=True)
        
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
    def forward(self, short_features, medium_features, long_features):
        _, short_hidden = self.short_encoder(short_features)
        _, medium_hidden = self.medium_encoder(medium_features)  
        _, long_hidden = self.long_encoder(long_features)
        
        combined = torch.cat([short_hidden[-1], medium_hidden[-1], long_hidden[-1]], dim=-1)
        return self.fusion(combined)

class AttentionGraphSAGE(MessagePassing):
    def __init__(self, in_channels, out_channels):
        super().__init__(aggr='add')
        self.lin = nn.Linear(in_channels, out_channels, bias=False)
        self.attention = nn.Linear(2 * out_channels + 1, 1) 

        nn.init.xavier_uniform_(self.lin.weight)
        nn.init.xavier_uniform_(self.attention.weight)
        self.attention.bias.data.zero_()
        
    def forward(self, x, edge_index, edge_attr):
        x = self.lin(x)
        
        row, col = edge_index
        x_i, x_j = x[row], x[col]
        
        edge_weights = edge_attr.unsqueeze(-1) if edge_attr.dim() == 1 else edge_attr
        alpha_input = torch.cat([x_i, x_j, edge_weights], dim=-1)
        attention_scores = self.attention(alpha_input).squeeze()
        attention_weights = softmax(attention_scores, row)
        
        return self.propagate(edge_index, x=x, attention=attention_weights)
    
    def message(self, x_j, attention):
        return attention.view(-1, 1) * x_j

class TemporalGNN(nn.Module):
    def __init__(self, feature_dim=Config.feature_dim, temporal_dim=Config.temporal_dim, gnn_dim=Config.gnn_dim):
        super().__init__()
        self.temporal_encoder = TemporalEncoder(feature_dim, temporal_dim)
        
        self.gnn1 = AttentionGraphSAGE(temporal_dim, gnn_dim)
        self.gnn2 = AttentionGraphSAGE(gnn_dim, gnn_dim)
        
        self.impact_head = nn.Linear(gnn_dim, 1)
        self.uncertainty_head = nn.Linear(gnn_dim, 1)
        
    def forward(self, short_features, medium_features, long_features, edge_index, edge_attr):
        
        temporal_emb = self.temporal_encoder(short_features, medium_features, long_features)

        if edge_index.shape[1] == 0:
            gnn_out2 = temporal_emb
        else:
            gnn_out1 = F.relu(self.gnn1(temporal_emb, edge_index, edge_attr))
            gnn_out2 = F.relu(self.gnn2(gnn_out1, edge_index, edge_attr))
            gnn_out2 = gnn_out2 + temporal_emb
            
        impact = torch.tanh(self.impact_head(gnn_out2)).squeeze()
        uncertainty = torch.sigmoid(self.uncertainty_head(gnn_out2)).squeeze()
        
        return impact, uncertainty
