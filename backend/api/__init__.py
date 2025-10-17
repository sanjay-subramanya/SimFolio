from fastapi import APIRouter

from .analyze import router as analysis_router
from .stocks import router as stock_router
from .health import router as status_router

router = APIRouter()
router.include_router(status_router)
router.include_router(stock_router)
router.include_router(analysis_router)
