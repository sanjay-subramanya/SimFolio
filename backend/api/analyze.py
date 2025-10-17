import torch
import numpy as np
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional

class PortfolioStock(BaseModel):
    stock: str
    shares: int

class ShockRequest(BaseModel):
    stock: str
    change_percent: float

class StockImpact(BaseModel):
    stock: str
    impact_percent: float
    correlation: Optional[float] = None

class AnalyzeResponse(BaseModel):
    shocked_stocks: List[str]
    impacts: List[StockImpact]
    portfolio_impact: float
    analysis_timestamp: str

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_impact(
    request: Request,
    portfolio: List[PortfolioStock],
    shocks: List[ShockRequest]
    ):
    """Analyze portfolio impact from single or multiple stock shocks"""
    try:
        if not portfolio:
            raise HTTPException(status_code=400, detail="Portfolio cannot be empty")
        
        if not shocks:
            raise HTTPException(status_code=400, detail="At least one shock required")
        
        selected_stocks = [stock_info.stock for stock_info in portfolio]
        total_shares = sum([stock_info.shares for stock_info in portfolio])
        for shock in shocks:
            if shock.stock not in selected_stocks:
                raise HTTPException(status_code=400, detail=f"Stock {shock.stock} not in portfolio")
        
        stock_weights = {stock_info.stock: stock_info.shares / total_shares for stock_info in portfolio}

        # Get multi-timeframe data
        ctx = request.app.state.ctx
        data = ctx.stock_data.get_multi_timeframe_data(selected_stocks)
        
        with torch.no_grad():
            short_features = data['timeframes']['short']['features']
            medium_features = data['timeframes']['medium']['features']
            long_features = data['timeframes']['long']['features']
            
            if short_features.dim() == 2:
                short_features = short_features.unsqueeze(1)
                medium_features = medium_features.unsqueeze(1)
                long_features = long_features.unsqueeze(1)
            
            impacts, uncertainties = ctx.model(
                short_features,
                medium_features,
                long_features,
                data['graph'].edge_index,
                data['graph'].edge_attr
            )
        
        impacts_np = impacts.cpu().numpy()
        uncertainties_np = uncertainties.cpu().numpy()
        
        stock_impacts = []
        weighted_impact = 0
        
        
        for i, stock_info in enumerate(portfolio):
            stock = stock_info.stock
            weight = stock_weights[stock]

            direct_shock = next((s for s in shocks if s.stock == stock), None)
            
            if direct_shock:
                final_impact = direct_shock.change_percent
            else:
                shock_effect = 0
                for shock in shocks:
                    shock_idx = selected_stocks.index(shock.stock)
                    correlation = data['correlations'].iloc[i, shock_idx]
                    shock_effect += shock.change_percent * 0.6 * correlation + impacts_np[i] * shock.change_percent * 0.4
                
                final_impact = shock_effect / len(shocks) if shocks else 0
            
            weighted_impact += final_impact * weight

            confidence = 1 - uncertainties_np[i]

            stock_impacts.append(StockImpact(
                stock=stock,
                impact_percent=round(final_impact, 2),
                correlation=round(data['correlations'].iloc[i].mean(), 3) if i < len(data['correlations']) else None
            ))
        
        return AnalyzeResponse(
            shocked_stocks=[s.stock for s in shocks],
            impacts=stock_impacts,
            portfolio_impact=round(weighted_impact, 2),
            analysis_timestamp=np.datetime64('now').astype(str)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

