"""
CLI主入口

提供命令行接口的主入口点。
"""

from .commands import create_cli_app


def main():
    """CLI主函数"""
    app = create_cli_app()
    app()


if __name__ == "__main__":
    main()
