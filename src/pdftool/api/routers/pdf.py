"""
PDF操作API路由
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..dependencies import get_pdf_operations, parse_page_list, validate_file_extension
from ..schemas.requests import (
    PageSelectionModeEnum,
    PDFMergeRequest,
    PDFPageSelectionRequest,
    WatermarkPositionEnum,
    WatermarkTypeEnum,
)
from ..schemas.responses import PDFInfoResponse, SuccessResponse
from ..services.pdf_service import PDFService

router = APIRouter(prefix="/api/v1/pdf", tags=["PDF操作"])


def get_pdf_service(pdf_ops=Depends(get_pdf_operations)) -> PDFService:
    """获取PDF服务实例"""
    return PDFService(pdf_ops)


@router.post(
    "/merge",
    summary="合并PDF文件",
    description="将多个PDF文件合并为一个文件",
    response_class=FileResponse,
)
async def merge_pdfs(
    files: List[UploadFile] = File(..., description="要合并的PDF文件列表"),
    preserve_bookmarks: bool = Form(True, description="是否保留书签"),
    preserve_metadata: bool = Form(True, description="是否保留元数据"),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    """
    合并多个PDF文件

    - **files**: 要合并的PDF文件列表（至少2个）
    - **preserve_bookmarks**: 是否保留书签信息
    - **preserve_metadata**: 是否保留元数据信息
    """
    # 验证文件
    for file in files:
        validate_file_extension(file.filename)

    # 创建请求对象
    request = PDFMergeRequest(
        preserve_bookmarks=preserve_bookmarks, preserve_metadata=preserve_metadata
    )

    # 执行合并
    result = await pdf_service.merge_pdfs(files, request)

    # 返回下载响应
    return pdf_service.create_download_response(result, "merged")


@router.post(
    "/info",
    response_model=PDFInfoResponse,
    summary="获取PDF文件信息",
    description="提取PDF文件的元数据和属性信息",
)
async def get_pdf_info(
    file: UploadFile = File(..., description="要分析的PDF文件"),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    """
    获取PDF文件详细信息

    - **file**: 要分析的PDF文件

    返回信息包括：
    - 页数
    - 标题
    - 作者
    - 创建日期
    - 文件大小
    """
    # 验证文件
    validate_file_extension(file.filename)

    # 获取PDF信息
    return await pdf_service.get_pdf_info(file)


@router.post(
    "/pages",
    summary="PDF页面选择和处理",
    description="统一的PDF页面选择功能，支持拆分、提取、合并等操作",
    response_class=FileResponse,
)
async def select_pages(
    file: UploadFile = File(..., description="要处理的PDF文件"),
    mode: PageSelectionModeEnum = Form(..., description="页面选择模式"),
    pages: Optional[str] = Form(None, description="指定页面列表，格式：'1,3,5' 或 '1-5'"),
    filename_prefix: Optional[str] = Form(None, description="输出文件名前缀"),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    """
    统一的PDF页面选择和处理

    - **file**: 要处理的PDF文件
    - **mode**: 页面选择模式：
        - `all`: 全部页面（每页单独文件）
        - `pages`: 指定页面列表（每页单独文件）
        - `single`: 将选中页面合并为单个文件
    - **pages**: 页面列表，支持格式：'1,3,5' 或 '1-5' 或 '1,3-5,8'
    - **filename_prefix**: 输出文件名前缀
    """
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

    # 执行页面选择
    result = await pdf_service.select_pages(file, request)

    # 返回下载响应
    if mode == PageSelectionModeEnum.ALL:
        filename = "all_pages"
    elif mode in [PageSelectionModeEnum.PAGES, PageSelectionModeEnum.SINGLE]:
        if page_list and len(page_list) == 1:
            filename = f"page_{page_list[0]}"
        else:
            filename = f"selected_pages"
    else:
        filename = "pdf_pages"

    return pdf_service.create_download_response(result, filename)


@router.get(
    "/formats",
    response_model=SuccessResponse,
    summary="获取支持的文件格式",
    description="返回API支持的文件格式列表",
)
async def get_supported_formats():
    """获取支持的文件格式"""
    return SuccessResponse(
        message="支持的文件格式",
        data={
            "input_formats": [".pdf"],
            "output_formats": [".pdf", ".zip"],
            "max_file_size": "100MB",
            "max_files_per_request": 50,
        },
    )


# REM: 实现水印功能接口
@router.post(
    "/watermark",
    response_class=JSONResponse,
    summary="添加水印",
    description="将水印添加到PDF文件中",
)
async def add_watermarks(
    file: UploadFile = File(..., description="要添加水印的PDF文件"),
    watermark_type: WatermarkTypeEnum = Form(..., description="水印类型: text/image"),
    watermark_text: Optional[str] = Form(None, description="文本水印内容"),
    font_size: Optional[int] = Form(None, description="字体大小"),
    font_color: Optional[str] = Form(None, description="字体颜色"),
    watermark_image: Optional[UploadFile] = File(None, description="图片水印文件"),
    image_scale: Optional[float] = Form(None, description="图片缩放比例"),
    position: WatermarkPositionEnum = Form(..., description="水印位置"),
    opacity: float = Form(..., description="透明度"),
    page_selection: PageSelectionModeEnum = Form(..., description="页面选择模式"),
    specific_pages: Optional[str] = Form(None, description="指定页面"),
    pdf_service: PDFService = Depends(get_pdf_service),
):
    validate_file_extension(file.filename)

    content = {
        "file": file.filename,
        "watermark_type": watermark_type,
        "watermark_text": watermark_text,
        "font_size": font_size,
        "font_color": font_color,
        "watermark_image": watermark_image.filename,
        "image_scale": image_scale,
        "position": position,
        "opacity": opacity,
        "page_selection": page_selection,
        "specific_pages": specific_pages,
    }

    print(content)

    raise NotImplementedError("水印功能尚未实现")
