"""
测试配置文件
配置pytest fixtures和测试环境
"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from PyPDF2 import PdfWriter

from pdftool.interfaces.web.application import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_app():
    """创建测试应用"""
    return app

@pytest.fixture
def client():
    """FastAPI TestClient"""
    return TestClient(app)

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_pdf_file(temp_dir: Path) -> Path:
    """创建示例PDF文件"""
    pdf_path = temp_dir / "sample.pdf"

    # 创建一个简单的PDF文件
    writer = PdfWriter()
    # 添加一个空白页
    from PyPDF2 import PageObject

    page = PageObject.create_blank_page(width=595, height=842)  # A4 size
    writer.add_page(page)

    with open(pdf_path, "wb") as f:
        writer.write(f)

    return pdf_path


@pytest.fixture
def sample_pdf_files(temp_dir: Path) -> list[Path]:
    """创建多个示例PDF文件用于合并测试"""
    pdf_files = []

    for i in range(3):
        pdf_path = temp_dir / f"sample_{i+1}.pdf"
        writer = PdfWriter()

        # 为每个PDF添加不同数量的页面
        for _ in range(i + 1):
            from PyPDF2 import PageObject

            page = PageObject.create_blank_page(width=595, height=842)
            writer.add_page(page)

        with open(pdf_path, "wb") as f:
            writer.write(f)

        pdf_files.append(pdf_path)

    return pdf_files


@pytest.fixture
def sample_image_file(temp_dir: Path) -> Path:
    """创建示例图片文件用于水印测试"""
    from PIL import Image

    img_path = temp_dir / "watermark.png"

    # 创建一个简单的图片
    img = Image.new("RGBA", (100, 50), (255, 0, 0, 128))  # 半透明红色
    img.save(img_path)

    return img_path


@pytest.fixture(autouse=True)
def setup_test_env():
    """设置测试环境"""
    # 设置测试环境变量
    os.environ["PDFTOOL_DEBUG"] = "true"
    os.environ["PDFTOOL_LOG_LEVEL"] = "DEBUG"
    yield
    # 清理环境变量
    os.environ.pop("PDFTOOL_DEBUG", None)
    os.environ.pop("PDFTOOL_LOG_LEVEL", None)
