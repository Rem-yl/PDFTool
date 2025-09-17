"""
健康检查路由
"""

import time
from datetime import datetime

from fastapi import APIRouter, Depends

from ..dependencies import get_settings
from ..schemas.responses import HealthResponse, SuccessResponse

router = APIRouter(prefix="/health", tags=["健康检查"])

# 应用启动时间
_start_time = time.time()


@router.get("", response_model=HealthResponse, summary="健康检查")
async def health_check(settings=Depends(get_settings)):
    """
    检查应用健康状态

    返回应用的基本信息和运行状态
    """
    uptime = time.time() - _start_time

    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.version,
        timestamp=datetime.now().isoformat(),
        uptime=uptime,
    )


@router.get("/ping", response_model=SuccessResponse, summary="简单连通性检查")
async def ping():
    """
    简单的连通性检查

    快速响应，用于负载均衡器健康检查
    """
    return SuccessResponse(message="pong", data={"timestamp": datetime.now().isoformat()})
