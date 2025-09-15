"""
API响应模型定义
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[str] = None


class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class PDFInfoResponse(BaseModel):
    """PDF信息响应模型"""
    pages: int
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None
    file_size: int


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    app_name: str
    version: str
    timestamp: str
    uptime: Optional[float] = None


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    filename: str
    size: int
    content_type: str
    upload_time: str