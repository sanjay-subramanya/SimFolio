from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/stocks")
async def get_available_stocks(request: Request):
    """Get all available stocks for user selection"""
    ctx = request.app.state.ctx
    return {
        "available_stocks": ctx.all_stocks,
        "stocks_count": len(ctx.all_stocks),
    }