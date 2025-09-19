"""
API文档和版本信息路由
"""

from fastapi import APIRouter, Depends

from ..dependencies import get_settings
from ..schemas.responses import SuccessResponse

router = APIRouter(prefix="/api", tags=["API文档"])


@router.get("/version", response_model=SuccessResponse, summary="获取API版本信息")
async def get_version(settings=Depends(get_settings)):
    """
    获取API版本和应用信息

    返回当前API的版本、构建信息和功能特性
    """
    return SuccessResponse(
        message="API版本信息",
        data={
            "version": settings.version,
            "app_name": settings.app_name,
            "api_version": "v1",
            "features": ["PDF合并", "PDF拆分", "PDF信息提取", "文件批量处理", "拖拽上传"],
            "supported_formats": {"input": [".pdf"], "output": [".pdf", ".zip"]},
            "limits": {
                "max_file_size": f"{settings.max_file_size / 1024 / 1024:.0f}MB",
                "max_files_per_request": 50,
            },
        },
    )


@router.get("/endpoints", response_model=SuccessResponse, summary="获取API端点列表")
async def get_endpoints():
    """
    获取所有可用的API端点

    返回API的完整端点列表和说明
    """
    endpoints = {
        "web": {
            "GET /": "功能选择主页",
            "GET /merge": "PDF合并页面",
            "GET /split": "PDF拆分页面",
            "GET /info": "PDF信息页面",
        },
        "api": {
            "POST /api/v1/pdf/merge": "合并PDF文件",
            "POST /api/v1/pdf/split": "拆分PDF文件",
            "POST /api/v1/pdf/info": "获取PDF信息",
            "GET /api/v1/pdf/formats": "支持的格式",
        },
        "system": {
            "GET /health": "健康检查",
            "GET /health/ping": "连通性检查",
            "GET /api/version": "版本信息",
            "GET /api/endpoints": "端点列表",
        },
    }

    return SuccessResponse(message="API端点列表", data=endpoints)


@router.get("/status", response_model=SuccessResponse, summary="获取API状态")
async def get_status(settings=Depends(get_settings)):
    """
    获取API服务状态

    返回服务运行状态和配置信息
    """
    import os
    import time  # noqa: F401

    import psutil

    try:
        # 系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        status_data = {
            "service": "running",
            "debug_mode": settings.debug,
            "temp_dir": str(settings.temp_dir),
            "temp_dir_exists": settings.temp_dir.exists(),
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "disk_usage": f"{disk.percent}%",
                "process_id": os.getpid(),
            },
            "config": {
                "max_file_size": f"{settings.max_file_size / 1024 / 1024:.0f}MB",
                "api_host": settings.api_host,
                "api_port": settings.api_port,
                "log_level": settings.log_level,
            },
        }

        return SuccessResponse(message="API服务状态正常", data=status_data)

    except Exception as e:
        return SuccessResponse(
            message="API服务状态检查失败",
            data={"service": "running", "error": str(e), "debug_mode": settings.debug},
        )
