"""
Web页面路由
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from ..dependencies import get_settings


# 模板目录
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(template_dir))

router = APIRouter(tags=["Web界面"])


@router.get("/", response_class=HTMLResponse, summary="功能选择主页")
async def home(
    request: Request,
    settings=Depends(get_settings)
):
    """
    功能选择主页面
    
    显示所有可用的PDF操作功能选项
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "version": settings.version
        }
    )


@router.get("/merge", response_class=HTMLResponse, summary="PDF合并页面")
async def merge_page(
    request: Request,
    settings=Depends(get_settings)
):
    """
    PDF合并操作页面
    
    提供文件上传和合并选项界面
    """
    return templates.TemplateResponse(
        "merge.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "show_back_button": True
        }
    )


@router.get("/pages", response_class=HTMLResponse, summary="PDF页面选择页面")
async def pages_page(
    request: Request,
    settings=Depends(get_settings)
):
    """
    统一的PDF页面选择操作页面
    
    提供文件上传和页面选择选项界面，支持拆分、提取、合并等操作
    """
    return templates.TemplateResponse(
        "pages.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "show_back_button": True
        }
    )


# 保持向后兼容的路由别名
@router.get("/split", response_class=HTMLResponse, summary="PDF拆分页面（重定向）")
async def split_page_redirect(request: Request):
    """重定向到统一页面选择界面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/pages?mode=range", status_code=302)


@router.get("/extract", response_class=HTMLResponse, summary="PDF页面提取页面（重定向）")
async def extract_page_redirect(request: Request):
    """重定向到统一页面选择界面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/pages?mode=pages", status_code=302)


@router.get("/info", response_class=HTMLResponse, summary="PDF信息页面")
async def info_page(
    request: Request,
    settings=Depends(get_settings)
):
    """
    PDF信息查看页面
    
    提供文件上传和信息展示界面
    """
    return templates.TemplateResponse(
        "info.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "show_back_button": True
        }
    )