"""
Health Check API
健康检查接口
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "EAIOS Backend"
    }


@router.get("/ping")
async def ping():
    """Ping测试"""
    return {"message": "pong"}
