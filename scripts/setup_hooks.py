#!/usr/bin/env python3
"""
Git Hooks 设置脚本
自动设置pre-commit hook来运行测试
"""

import shutil
import sys
from pathlib import Path


def setup_git_hooks():
    """设置Git hooks"""
    project_root = Path(__file__).parent.parent
    hooks_dir = project_root / ".git" / "hooks"

    if not hooks_dir.exists():
        print("❌ .git/hooks 目录不存在，请确保在Git仓库中运行")
        return False

    # 源文件和目标文件
    source_hook = hooks_dir / "pre-commit-tests"
    target_hook = hooks_dir / "pre-commit"
    backup_hook = hooks_dir / "pre-commit.backup"

    # 检查源文件是否存在
    if not source_hook.exists():
        print("❌ pre-commit-tests hook文件不存在")
        return False

    # 备份现有的pre-commit hook
    if target_hook.exists():
        if backup_hook.exists():
            backup_hook.unlink()
        shutil.copy2(target_hook, backup_hook)
        print(f"📦 已备份现有hook到: {backup_hook}")

    # 复制新的hook
    shutil.copy2(source_hook, target_hook)
    target_hook.chmod(0o755)

    print("✅ Pre-commit hook设置完成")
    print(f"📁 Hook位置: {target_hook}")

    return True


def restore_git_hooks():
    """恢复原始的Git hooks"""
    project_root = Path(__file__).parent.parent
    hooks_dir = project_root / ".git" / "hooks"

    target_hook = hooks_dir / "pre-commit"
    backup_hook = hooks_dir / "pre-commit.backup"

    if backup_hook.exists():
        if target_hook.exists():
            target_hook.unlink()
        shutil.copy2(backup_hook, target_hook)
        backup_hook.unlink()
        print("✅ 已恢复原始的pre-commit hook")
    else:
        if target_hook.exists():
            target_hook.unlink()
        print("✅ 已移除自定义的pre-commit hook")


def check_hook_status():
    """检查hook状态"""
    project_root = Path(__file__).parent.parent
    hooks_dir = project_root / ".git" / "hooks"

    target_hook = hooks_dir / "pre-commit"
    backup_hook = hooks_dir / "pre-commit.backup"
    source_hook = hooks_dir / "pre-commit-tests"

    print("🔍 Git Hooks 状态检查:")
    print(f"  项目根目录: {project_root}")
    print(f"  Hooks目录: {hooks_dir}")
    print()

    if target_hook.exists():
        print("✅ pre-commit hook已存在")
        # 简单检查是否是我们的hook
        content = target_hook.read_text()
        if "PDFTool" in content:
            print("  📋 检测到PDFTool测试hook")
        else:
            print("  📋 检测到其他pre-commit hook")
    else:
        print("❌ pre-commit hook不存在")

    if backup_hook.exists():
        print("📦 发现备份的hook文件")

    if source_hook.exists():
        print("📁 测试hook模板文件存在")

    print()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="PDFTool Git Hooks 设置工具")
    parser.add_argument("action", choices=["install", "uninstall", "status"], help="操作类型")

    args = parser.parse_args()

    print("🔧 PDFTool Git Hooks 设置工具")
    print()

    if args.action == "install":
        if setup_git_hooks():
            print()
            print("🎉 安装完成!")
            print("💡 现在每次提交时都会自动运行测试")
            print("   如果测试失败，提交将被阻止")
            print("   使用 'git commit --no-verify' 可以跳过检查")
        else:
            print("💥 安装失败!")
            sys.exit(1)

    elif args.action == "uninstall":
        restore_git_hooks()
        print()
        print("🎉 卸载完成!")
        print("💡 提交时将不再自动运行测试")

    elif args.action == "status":
        check_hook_status()

    print()


if __name__ == "__main__":
    main()
