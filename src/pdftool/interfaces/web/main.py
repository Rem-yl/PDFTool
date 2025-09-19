"""
PDFTool API主入口文件
"""

import uvicorn

from ...common.utils.logging import get_logger
from ...config.settings import settings
from .application import app  # noqa: F401

logger = get_logger("api.main")


def main() -> None:
    """
    API服务主入口点
    """
    logger.info("启动PDFTool API服务...")
    logger.info(
        f"配置信息: 主机={settings.api_host}, 端口={settings.api_port}, "
        f"调试模式={settings.debug}, 工作进程={settings.api_workers}"
    )

    try:
        uvicorn.run(
            "pdftool.interfaces.web.application:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug,
            workers=settings.api_workers if not settings.debug else 1,
            log_level=settings.log_level.lower(),
            access_log=True,
            server_header=False,
            date_header=False,
        )
    except Exception as e:
        logger.error(f"启动API服务失败: {str(e)}")
        raise


if __name__ == "__main__":
    main()
