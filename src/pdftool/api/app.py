"""
FastAPI应用工厂
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ..config.settings import settings
from ..utils.logging import get_logger, setup_logging
from .middleware.cors import setup_cors
from .middleware.error_handler import ErrorHandlerMiddleware, setup_error_handlers
from .middleware.logging import setup_logging_middleware
from .routers import docs, health, pdf, web

# 设置日志
setup_logging()
logger = get_logger("api.app")


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例

    Returns:
        FastAPI: 配置好的FastAPI应用实例
    """

    # 创建FastAPI应用
    app = FastAPI(
        title=f"{settings.app_name} API",
        description="专业的PDF操作工具API服务，提供合并、拆分、信息提取等功能",
        version=settings.version,
        debug=settings.debug,
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
        openapi_url="/api/openapi.json" if settings.debug else None,
    )

    # 设置中间件
    setup_middleware(app)

    # 设置路由
    setup_routers(app)

    # 设置静态文件
    setup_static_files(app)

    # 设置错误处理
    setup_error_handlers(app)

    logger.info(f"FastAPI应用创建完成 - {settings.app_name} v{settings.version}")

    return app


def setup_middleware(app: FastAPI) -> None:
    """设置中间件"""

    # CORS中间件
    setup_cors(app)

    # 错误处理中间件
    app.add_middleware(ErrorHandlerMiddleware)

    # 请求日志中间件
    setup_logging_middleware(app)

    logger.info("中间件设置完成")


def setup_routers(app: FastAPI) -> None:
    """设置路由"""

    # Web界面路由
    app.include_router(web.router)

    # API路由
    app.include_router(pdf.router)

    # 健康检查路由
    app.include_router(health.router)

    # API文档路由
    app.include_router(docs.router)

    logger.info("路由设置完成")


def setup_static_files(app: FastAPI) -> None:
    """设置静态文件服务"""

    # 静态文件目录
    static_dir = Path(__file__).parent / "templates" / "static"

    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        logger.info(f"静态文件服务设置完成: {static_dir}")
    else:
        logger.warning(f"静态文件目录不存在: {static_dir}")


def get_app_info() -> dict:
    """
    获取应用信息

    Returns:
        dict: 应用信息字典
    """
    return {
        "name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "temp_dir": str(settings.temp_dir),
        "max_file_size": settings.max_file_size,
        "log_level": settings.log_level,
    }


# 创建应用实例
app = create_app()


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("PDFTool API服务启动")
    logger.info(f"应用信息: {get_app_info()}")

    # 确保临时目录存在
    settings.temp_dir.mkdir(exist_ok=True)
    logger.info(f"临时目录准备完成: {settings.temp_dir}")


# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("PDFTool API服务关闭")


# 根路径重定向到健康检查
@app.get("/api", include_in_schema=False)
async def api_root():
    """API根路径"""
    return {
        "message": "PDFTool API Service",
        "version": settings.version,
        "docs": "/api/docs",
        "health": "/health",
    }
