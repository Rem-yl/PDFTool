"""
Web页面路由
"""

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..dependencies import get_settings

# 模板目录
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(template_dir))

router = APIRouter(tags=["Web界面"])


@router.get("/", response_class=HTMLResponse, summary="功能选择主页")
async def home(request: Request, settings=Depends(get_settings)):
    """
    功能选择主页面

    显示所有可用的PDF操作功能选项
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.app_name, "version": settings.version},
    )


@router.get("/merge", response_class=HTMLResponse, summary="PDF合并页面")
async def merge_page(request: Request, settings=Depends(get_settings)):
    """
    PDF合并操作页面

    提供文件上传和合并选项界面
    """
    return templates.TemplateResponse(
        "merge.html", {"request": request, "app_name": settings.app_name, "show_back_button": True}
    )


@router.get("/pages", response_class=HTMLResponse, summary="PDF页面选择页面")
async def pages_page(request: Request, settings=Depends(get_settings)):
    """
    统一的PDF页面选择操作页面

    提供文件上传和页面选择选项界面，支持拆分、提取、合并等操作
    """
    return templates.TemplateResponse(
        "pages.html", {"request": request, "app_name": settings.app_name, "show_back_button": True}
    )


@router.get("/info", response_class=HTMLResponse, summary="PDF信息页面")
async def info_page(request: Request, settings=Depends(get_settings)):
    """
    PDF信息查看页面

    提供文件上传和信息展示界面
    """
    return templates.TemplateResponse(
        "info.html", {"request": request, "app_name": settings.app_name, "show_back_button": True}
    )


@router.get("/watermark", response_class=HTMLResponse, summary="添加水印页面")
async def add_watermark_page(request: Request, settings=Depends(get_settings)):
    """
    PDF添加水印功能页面

    支持上传图片以及输入文字添加水印
    """
    return templates.TemplateResponse(
        "watermark.html",
        {"request": request, "app_name": settings.app_name, "show_back_button": True},
    )
