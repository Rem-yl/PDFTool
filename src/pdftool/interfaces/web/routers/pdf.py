"""
PDF操作API路由 - 新架构版本 (v2)
使用可扩展的服务注册模式
"""

from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..dependencies import (
    get_service_registry,
    parse_page_list,
    validate_file_extension,
)
from ..schemas.requests import (
    PageSelectionModeEnum,
    PDFMergeRequest,
    PDFPageSelectionRequest,
    WatermarkPositionEnum,
    WatermarkRequest,
    WatermarkTypeEnum,
)
from ..schemas.responses import PDFInfoResponse, SuccessResponse
from ..service_registry import ServiceRegistry

router = APIRouter(prefix="/api/v1/pdf", tags=["PDF操作"])


@router.post(
    "/merge",
    summary="合并PDF文件",
    description="将多个PDF文件合并为一个文件",
    response_class=FileResponse,
)
async def merge_pdfs_v2(
    files: List[UploadFile] = File(..., description="要合并的PDF文件列表"),
    preserve_bookmarks: bool = Form(True, description="是否保留书签"),
    preserve_metadata: bool = Form(True, description="是否保留元数据"),
    service_registry: ServiceRegistry = Depends(get_service_registry),
):
    """合并多个PDF文件 - 使用新架构"""
    # 验证文件
    for file in files:
        validate_file_extension(file.filename)

    # 创建请求对象
    request = PDFMergeRequest(
        preserve_bookmarks=preserve_bookmarks, preserve_metadata=preserve_metadata
    )

    # 获取合并服务处理器
    merge_handler = service_registry.get_handler("merge")

    # 执行合并
    result = await merge_handler.handle(files, request)

    # 返回下载响应
    return merge_handler.create_download_response(result, "merged")


@router.post(
    "/info",
    response_model=PDFInfoResponse,
    summary="获取PDF文件信息",
    description="提取PDF文件的元数据和属性信息",
)
async def get_pdf_info_v2(
    file: UploadFile = File(..., description="要分析的PDF文件"),
    service_registry: ServiceRegistry = Depends(get_service_registry),
):
    """获取PDF文件详细信息 - 使用新架构"""
    # 验证文件
    validate_file_extension(file.filename)

    # 获取信息服务处理器
    info_handler = service_registry.get_handler("info")

    # 获取PDF信息
    result = await info_handler.handle([file], request=None)

    # 从 OperationResult 中解析 PDFInfoResponse
    if result.success and result.details:
        import json

        info_data = json.loads(result.details)
        return PDFInfoResponse(**info_data)

    raise HTTPException(status_code=500, detail=result.message)


@router.post(
    "/pages",
    summary="PDF页面选择和处理",
    description="统一的PDF页面选择功能，支持拆分、提取、合并等操作",
    response_class=FileResponse,
)
async def select_pages_v2(
    file: UploadFile = File(..., description="要处理的PDF文件"),
    mode: PageSelectionModeEnum = Form(..., description="页面选择模式"),
    pages: Optional[str] = Form(None, description="指定页面列表，格式：'1,3,5' 或 '1-5'"),
    filename_prefix: Optional[str] = Form(None, description="输出文件名前缀"),
    service_registry: ServiceRegistry = Depends(get_service_registry),
):
    """统一的PDF页面选择和处理 - 使用新架构"""
    validate_file_extension(file.filename)

    # 解析页面列表（如果需要）
    page_list = None
    if pages and mode in [PageSelectionModeEnum.PAGES, PageSelectionModeEnum.SINGLE]:
        try:
            page_list = parse_page_list(pages)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="页面格式错误，请使用 '1,3,5' 或 '1-5' 格式"
            )

    # 创建请求对象
    request = PDFPageSelectionRequest(mode=mode, pages=page_list, filename_prefix=filename_prefix)

    # 获取分割服务处理器
    split_handler = service_registry.get_handler("split")

    # 执行页面选择
    result = await split_handler.handle([file], request)

    # 返回下载响应
    if mode == PageSelectionModeEnum.ALL:
        filename = "all_pages"
    elif mode in [PageSelectionModeEnum.PAGES, PageSelectionModeEnum.SINGLE]:
        if page_list and len(page_list) == 1:
            filename = f"page_{page_list[0]}"
        else:
            filename = "selected_pages"
    else:
        filename = "pdf_pages"

    return split_handler.create_download_response(result, filename)


@router.post(
    "/watermark",
    response_class=FileResponse,
    summary="添加水印",
    description="将水印添加到PDF文件中",
)
async def add_watermark_v2(
    file: UploadFile = File(..., description="要添加水印的PDF文件"),
    watermark_type: WatermarkTypeEnum = Form(..., description="水印类型: text/image"),
    watermark_text: Optional[str] = Form(None, description="文本水印内容"),
    font_size: Optional[int] = Form(36, description="字体大小"),
    font_color: Optional[str] = Form("#000000", description="字体颜色"),
    watermark_image: Optional[UploadFile] = File(None, description="图片水印文件"),
    image_scale: Optional[float] = Form(100, description="图片缩放比例"),
    position: WatermarkPositionEnum = Form(..., description="水印位置"),
    opacity: float = Form(..., description="透明度(0.1-1.0)"),
    page_selection: PageSelectionModeEnum = Form(..., description="页面选择模式"),
    specific_pages: Optional[str] = Form(None, description="指定页面"),
    service_registry: ServiceRegistry = Depends(get_service_registry),
):
    """添加水印到PDF文件 - 使用新架构"""
    # 验证文件
    validate_file_extension(file.filename)

    # 验证水印图片文件
    if watermark_type == WatermarkTypeEnum.IMAGE and watermark_image:
        allowed_image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
        image_ext = Path(watermark_image.filename or "").suffix.lower()
        if image_ext not in allowed_image_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"图片格式不支持，支持的格式: {', '.join(allowed_image_extensions)}",
            )

    # 创建请求对象
    try:
        request = WatermarkRequest(
            watermark_type=watermark_type,
            position=position,
            opacity=opacity / 100.0,  # 前端传百分比，转换为小数
            watermark_text=watermark_text,
            font_size=font_size,
            font_color=font_color,
            image_scale=image_scale,
            page_selection=page_selection,
            specific_pages=specific_pages,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"参数验证失败: {str(e)}")

    # 获取水印服务处理器
    watermark_handler = service_registry.get_handler("watermark")

    # 执行水印添加
    result = await watermark_handler.handle([file], request, watermark_image)

    # 返回下载响应
    filename = f"watermarked_{Path(file.filename or 'document').stem}"
    return watermark_handler.create_download_response(result, filename)


@router.get(
    "/services",
    response_model=SuccessResponse,
    summary="获取可用服务列表",
    description="返回所有已注册的服务列表",
)
async def list_services(service_registry: ServiceRegistry = Depends(get_service_registry)):
    """获取可用服务列表 - 展示架构的扩展能力"""
    return SuccessResponse(
        message="可用服务列表",
        data={
            "services": service_registry.list_services(),
            "architecture": "Extensible Service Registry Pattern",
        },
    )
