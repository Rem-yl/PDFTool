"""
全局错误处理中间件
"""

import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ....common.exceptions import (
    PDFFileNotFoundError,
    PDFProcessingError,
    PDFToolError,
    PDFValidationError,
)
from ....common.utils.logging import get_logger
from ..schemas.responses import ErrorResponse

logger = get_logger("api.error_handler")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """处理异常并返回统一格式的错误响应"""

        # PDF工具特定错误
        if isinstance(exc, PDFValidationError):
            logger.warning(f"PDF validation error: {str(exc)}")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    message="PDF文件验证失败", error_code="PDF_VALIDATION_ERROR", details=str(exc)
                ).dict(),
            )

        elif isinstance(exc, PDFFileNotFoundError):
            logger.warning(f"PDF file not found: {str(exc)}")
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(
                    message="PDF文件未找到", error_code="PDF_FILE_NOT_FOUND", details=str(exc)
                ).dict(),
            )

        elif isinstance(exc, PDFProcessingError):
            logger.error(f"PDF processing error: {str(exc)}")
            return JSONResponse(
                status_code=422,
                content=ErrorResponse(
                    message="PDF处理失败", error_code="PDF_PROCESSING_ERROR", details=str(exc)
                ).dict(),
            )

        elif isinstance(exc, PDFToolError):
            logger.error(f"PDFTool error: {str(exc)}")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    message="PDF操作失败", error_code="PDF_TOOL_ERROR", details=str(exc)
                ).dict(),
            )

        # HTTP错误
        elif isinstance(exc, HTTPException):
            logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse(
                    message=exc.detail, error_code=f"HTTP_{exc.status_code}"
                ).dict(),
            )

        # 未知错误
        else:
            logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    message="服务器内部错误",
                    error_code="INTERNAL_SERVER_ERROR",
                    details=(
                        "请联系管理员" if not logger.isEnabledFor(10) else str(exc)
                    ),  # DEBUG level
                ).dict(),
            )


def setup_error_handlers(app: FastAPI) -> None:
    """设置全局错误处理器"""

    @app.exception_handler(PDFToolError)
    async def pdftool_exception_handler(request: Request, exc: PDFToolError):
        """PDF工具异常处理器"""
        logger.error(f"PDFTool exception: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message="PDF操作失败", error_code="PDF_TOOL_ERROR", details=str(exc)
            ).dict(),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """值错误处理器"""
        logger.warning(f"Value error: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                message="参数错误", error_code="VALUE_ERROR", details=str(exc)
            ).dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="服务器内部错误",
                error_code="INTERNAL_SERVER_ERROR",
                details=str(exc) if logger.isEnabledFor(10) else "请联系管理员",  # DEBUG level
            ).dict(),
        )
