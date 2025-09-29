#!/usr/bin/env python3
"""
PDFTool 测试运行脚本
一键运行所有测试，支持多种运行模式和配置选项
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List


class TestRunner:
    """测试运行器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        self.src_dir = project_root / "src"

    def setup_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")

        # 设置环境变量
        env_vars = {
            "PDFTOOL_DEBUG": "true",
            "PDFTOOL_LOG_LEVEL": "DEBUG",
            "PDFTOOL_TEMP_DIR": "temp_test",
            "PYTHONPATH": str(self.project_root / "src"),
        }

        for key, value in env_vars.items():
            os.environ[key] = value

        print("✓ 环境变量设置完成")

    def check_dependencies(self) -> bool:
        """检查依赖是否安装"""
        print("📦 检查测试依赖...")

        required_packages = ["pytest", "pytest-cov", "pytest-asyncio", "httpx", "fastapi", "PyPDF2"]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install -r requirements.txt")
            return False

        print("✓ 所有依赖包已安装")
        return True

    def run_linting(self) -> bool:
        """运行代码检查"""
        print("🔍 运行代码检查...")

        directories = ["src", "tests", "scripts"]

        commands = [
            [
                "python",
                "-m",
                "flake8",
                *directories,
                "--max-line-length=100",
                "--extend-ignore=E203,W503",
            ],
            # ["python", "-m", "mypy", *directories, "--ignore-missing-imports"], #REM: mypy类型检查待修复
            ["python", "-m", "black", *directories],
            ["python", "-m", "isort", *directories, "--profile", "black", "--filter-files"],
        ]

        for cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
                if result.returncode != 0:
                    print(f"❌ {' '.join(cmd)} 失败:")
                    print(result.stdout)
                    print(result.stderr)
                    return False
            except FileNotFoundError:
                print(f"⚠️  跳过 {cmd[2]} (未安装)")
                continue

        print("✓ 代码检查通过")
        return True

    def run_basic_tests(self) -> bool:
        """运行基础测试"""
        print("🧪 运行基础环境测试...")

        cmd = ["python", "-m", "pytest", str(self.tests_dir / "test_simple.py"), "-v", "--tb=short"]

        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ 基础测试失败:")
            print(result.stdout)
            print(result.stderr)
            return False

        print("✓ 基础测试通过")
        return True

    def run_all_tests(self, coverage: bool = True, verbose: bool = True) -> bool:
        """运行所有测试"""
        print("🧪 运行完整测试套件...")

        cmd = ["python", "-m", "pytest", str(self.tests_dir)]

        if verbose:
            cmd.append("-v")

        if coverage:
            cmd.extend(
                [
                    "--cov=src/pdftool",
                    "--cov-report=term-missing",
                    "--cov-report=html:htmlcov",
                    "--cov-fail-under=50",  # 最低覆盖率要求
                ]
            )

        cmd.extend(["--tb=short"])

        start_time = time.time()

        result = subprocess.run(cmd, cwd=self.project_root)

        end_time = time.time()
        duration = end_time - start_time

        if result.returncode == 0:
            print(f"✓ 所有测试通过 (耗时: {duration:.2f}s)")
            if coverage:
                print("📊 覆盖率报告已生成: htmlcov/index.html")
            return True
        else:
            print(f"❌ 测试失败 (耗时: {duration:.2f}s)")
            return False

    def run_specific_tests(self, test_files: List[str]) -> bool:
        """运行指定的测试文件"""
        print(f"🧪 运行指定测试: {', '.join(test_files)}")

        cmd = ["python", "-m", "pytest"] + test_files + ["-v", "--tb=short"]

        result = subprocess.run(cmd, cwd=self.project_root)

        return result.returncode == 0

    def clean_test_artifacts(self):
        """清理测试产生的文件"""
        print("🧹 清理测试文件...")

        patterns_to_clean = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            ".pytest_cache",
            "temp_test",
            ".coverage",
        ]

        import shutil
        from glob import glob

        for pattern in patterns_to_clean:
            for path in glob(str(self.project_root / pattern), recursive=True):
                path_obj = Path(path)
                try:
                    if path_obj.is_dir():
                        shutil.rmtree(path_obj)
                    else:
                        path_obj.unlink()
                except (OSError, PermissionError):
                    pass

        print("✓ 清理完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PDFTool 测试运行器")
    parser.add_argument(
        "--mode",
        choices=["basic", "full", "lint", "specific"],
        default="full",
        help="测试模式 (默认: full)",
    )
    parser.add_argument("--no-coverage", action="store_true", help="跳过覆盖率检查")
    parser.add_argument("--no-lint", action="store_true", help="跳过代码检查")
    parser.add_argument("--clean", action="store_true", help="清理测试文件后退出")
    parser.add_argument("--files", nargs="+", help="指定要运行的测试文件")
    parser.add_argument("--quiet", action="store_true", help="安静模式，减少输出")

    args = parser.parse_args()

    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    runner = TestRunner(project_root)

    # 如果只是清理，执行清理后退出
    if args.clean:
        runner.clean_test_artifacts()
        return 0

    print("🚀 PDFTool 测试运行器启动")
    print(f"📁 项目根目录: {project_root}")
    print(f"🧪 测试目录: {runner.tests_dir}")
    print()

    # 设置环境
    runner.setup_environment()

    # 检查依赖
    if not runner.check_dependencies():
        return 1

    success = True

    try:
        # 根据模式运行不同的测试
        if args.mode == "basic":
            success = runner.run_basic_tests()

        elif args.mode == "lint":
            success = runner.run_linting()

        elif args.mode == "specific":
            if not args.files:
                print("❌ 指定模式需要提供测试文件")
                return 1
            success = runner.run_specific_tests(args.files)

        elif args.mode == "full":
            # 完整测试流程
            if not args.no_lint:
                if not runner.run_linting():
                    if not args.quiet:
                        print("⚠️  代码检查失败，但继续运行测试...")

            # 先运行基础测试
            if not runner.run_basic_tests():
                print("❌ 基础测试失败，跳过完整测试")
                return 1

            # 运行完整测试
            success = runner.run_all_tests(coverage=not args.no_coverage, verbose=not args.quiet)

    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        return 130

    except Exception as e:
        print(f"❌ 测试运行出错: {e}")
        return 1

    finally:
        # 清理临时文件
        if not args.quiet:
            runner.clean_test_artifacts()

    # 输出结果
    print()
    if success:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("💥 测试失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
