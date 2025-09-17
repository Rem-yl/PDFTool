"""
CORS中间件配置
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ....config.settings import settings


def setup_cors(app: FastAPI) -> None:
    """配置CORS中间件"""

    # 根据环境配置不同的CORS策略
    if settings.debug:
        # 开发环境 - 宽松的CORS策略
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # 生产环境 - 严格的CORS策略
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://pdftool.example.com",
                "https://www.pdftool.example.com",
            ],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=[
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Accept",
                "Origin",
            ],
            expose_headers=["Content-Disposition"],
        )
