import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

@router.get("/health")
async def health_check(request: Request):
    """API health check with model status"""
    try:
        ctx = request.app.state.ctx
        model_exists = os.path.exists(ctx.model_path)
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "model_exists": model_exists,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")