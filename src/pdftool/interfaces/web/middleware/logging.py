"""
请求日志中间件
"""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ....common.utils.logging import get_logger

logger = get_logger("api.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # 记录请求开始
        start_time = time.time()
        client_ip = self.get_client_ip(request)

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} " f"from {client_ip} - Start"
        )

        # 处理请求
        try:
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求完成
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} "
                f"- {response.status_code} - {process_time:.3f}s"
            )

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as exc:
            # 记录请求异常
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} "
                f"- ERROR: {str(exc)} - {process_time:.3f}s"
            )
            raise

    def get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 优先从代理头获取真实IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 回退到直接连接IP
        return request.client.host if request.client else "unknown"


def setup_logging_middleware(app: FastAPI) -> None:
    """设置日志中间件"""
    app.add_middleware(RequestLoggingMiddleware)
