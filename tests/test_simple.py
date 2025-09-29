"""
简单的测试验证测试环境是否正常工作, 测试包括:
1. pytest是否正常工作;
2. pdftool基础模块是否能够导入;
3. PyPDF2模块是否正常工作;
"""

import pytest


def test_basic_functionality():
    """基本功能测试"""
    assert 1 + 1 == 2


def test_imports():
    """测试重要模块是否可以导入"""
    try:
        from pdftool.interfaces.web.application import app

        assert app is not None
        print("✓ FastAPI应用导入成功")
    except ImportError as e:
        pytest.fail(f"无法导入FastAPI应用: {e}")

    try:
        from PyPDF2 import PdfWriter

        writer = PdfWriter()
        assert writer is not None
        print("✓ PyPDF2导入成功")
    except ImportError as e:
        pytest.fail(f"无法导入PyPDF2: {e}")

    try:
        import httpx  # noqa: F401

        print("✓ httpx导入成功")
    except ImportError as e:
        pytest.fail(f"无法导入httpx: {e}")


def test_app_creation():
    """测试应用创建"""
    from pdftool.interfaces.web.application import app

    assert hasattr(app, "routes")
    assert len(app.routes) > 0
    print(f"✓ 应用有 {len(app.routes)} 个路由")


def test_basic_pdf_creation():
    """测试基本PDF创建功能"""
    import tempfile
    from pathlib import Path

    from PyPDF2 import PageObject, PdfWriter

    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "test.pdf"

        writer = PdfWriter()
        page = PageObject.create_blank_page(width=595, height=842)
        writer.add_page(page)

        with open(pdf_path, "wb") as f:
            writer.write(f)

        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        print("✓ 基本PDF创建功能正常")


if __name__ == "__main__":
    test_basic_functionality()
    test_imports()
    test_app_creation()
    test_basic_pdf_creation()
    print("所有基本测试通过！")
