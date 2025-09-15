"""
PDF操作API路由
"""

from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Depends, Form, HTTPException
from fastapi.responses import FileResponse

from ..dependencies import get_pdf_operations, validate_file_size, validate_file_extension
from ..services.pdf_service import PDFService
from ..schemas.requests import PDFSplitRequest, PDFMergeRequest, PDFExtractRequest, PDFPageSelectionRequest, SplitModeEnum, PageSelectionModeEnum
from ..schemas.responses import PDFInfoResponse, SuccessResponse


router = APIRouter(prefix="/api/v1/pdf", tags=["PDF操作"])


def get_pdf_service(pdf_ops=Depends(get_pdf_operations)) -> PDFService:
    """获取PDF服务实例"""
    return PDFService(pdf_ops)


@router.post(
    "/merge",
    summary="合并PDF文件",
    description="将多个PDF文件合并为一个文件",
    response_class=FileResponse
)
async def merge_pdfs(
    files: List[UploadFile] = File(..., description="要合并的PDF文件列表"),
    preserve_bookmarks: bool = Form(True, description="是否保留书签"),
    preserve_metadata: bool = Form(True, description="是否保留元数据"),
    pdf_service: PDFService = Depends(get_pdf_service)
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
        preserve_bookmarks=preserve_bookmarks,
        preserve_metadata=preserve_metadata
    )
    
    # 执行合并
    result = await pdf_service.merge_pdfs(files, request)
    
    # 返回下载响应
    return pdf_service.create_download_response(result, "merged")


@router.post(
    "/split",
    summary="拆分PDF文件",
    description="将PDF文件拆分成多个页面或指定范围",
    response_class=FileResponse
)
async def split_pdf(
    file: UploadFile = File(..., description="要拆分的PDF文件"),
    mode: SplitModeEnum = Form(..., description="拆分模式：all(每页单独) 或 range(指定范围)"),
    start_page: Optional[int] = Form(None, description="起始页码（range模式需要）"),
    end_page: Optional[int] = Form(None, description="结束页码（range模式可选）"),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """
    拆分PDF文件
    
    - **file**: 要拆分的PDF文件
    - **mode**: 拆分模式
        - `all`: 每页单独拆分
        - `range`: 指定页面范围拆分
    - **start_page**: 起始页码（range模式必需）
    - **end_page**: 结束页码（range模式可选，默认到最后一页）
    """
    # 验证文件
    validate_file_extension(file.filename)
    
    # 创建请求对象
    request = PDFSplitRequest(
        mode=mode,
        start_page=start_page,
        end_page=end_page
    )
    
    # 验证range模式参数
    if mode == SplitModeEnum.RANGE and start_page is None:
        raise HTTPException(
            status_code=400,
            detail="range模式必须指定start_page参数"
        )
    
    # 执行拆分
    result = await pdf_service.split_pdf(file, request)
    
    # 返回下载响应
    filename = "split_pages" if mode == SplitModeEnum.ALL else "split_range"
    return pdf_service.create_download_response(result, filename)


@router.post(
    "/info",
    response_model=PDFInfoResponse,
    summary="获取PDF文件信息",
    description="提取PDF文件的元数据和属性信息"
)
async def get_pdf_info(
    file: UploadFile = File(..., description="要分析的PDF文件"),
    pdf_service: PDFService = Depends(get_pdf_service)
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
    "/extract",
    summary="提取PDF指定页面",
    description="从PDF文件中提取指定的页面",
    response_class=FileResponse
)
async def extract_pages(
    file: UploadFile = File(..., description="要提取页面的PDF文件"),
    pages: str = Form(..., description="要提取的页面列表，格式：'1,3,5' 或 '1-5'"),
    filename_prefix: Optional[str] = Form(None, description="输出文件名前缀"),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """
    提取PDF指定页面
    
    - **file**: 要处理的PDF文件
    - **pages**: 页面列表，支持两种格式：
        - 逗号分隔：'1,3,5,7' 
        - 范围格式：'1-5' 或 '1,3-5,8'
    - **filename_prefix**: 输出文件名前缀（可选）
    
    返回提取的页面文件（单页时返回PDF，多页时返回ZIP包）
    """
    # 验证文件
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    validate_file_extension(file.filename)
    
    try:
        # 解析页面列表
        page_list = []
        for part in pages.split(','):
            part = part.strip()
            if '-' in part:
                # 处理范围格式 "1-5"
                start, end = map(int, part.split('-'))
                if start > end:
                    raise HTTPException(
                        status_code=400,
                        detail=f"页面范围错误: {start}-{end}，起始页不能大于结束页"
                    )
                page_list.extend(range(start, end + 1))
            else:
                # 处理单个页面
                page_list.append(int(part))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="页面格式错误，请使用 '1,3,5' 或 '1-5' 格式"
        )
    
    # 创建请求对象
    request = PDFExtractRequest(
        pages=page_list,
        filename_prefix=filename_prefix
    )
    
    # 执行页面提取
    result = await pdf_service.extract_pages(file, request)
    
    # 返回下载响应
    if len(page_list) == 1:
        filename = f"page_{page_list[0]}"
    else:
        filename = f"pages_{min(page_list)}-{max(page_list)}"
    
    return pdf_service.create_download_response(result, filename)


@router.post(
    "/pages",
    summary="PDF页面选择和处理",
    description="统一的PDF页面选择功能，支持拆分、提取、合并等操作",
    response_class=FileResponse
)
async def select_pages(
    file: UploadFile = File(..., description="要处理的PDF文件"),
    mode: PageSelectionModeEnum = Form(..., description="页面选择模式"),
    pages: Optional[str] = Form(None, description="指定页面列表，格式：'1,3,5' 或 '1-5'"),
    filename_prefix: Optional[str] = Form(None, description="输出文件名前缀"),
    pdf_service: PDFService = Depends(get_pdf_service)
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
    # 验证文件
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    validate_file_extension(file.filename)
    
    # 解析页面列表（如果需要）
    page_list = None
    if pages and mode in [PageSelectionModeEnum.PAGES, PageSelectionModeEnum.SINGLE]:
        try:
            page_list = []
            for part in pages.split(','):
                part = part.strip()
                if '-' in part:
                    # 处理范围格式 "1-5"
                    start, end = map(int, part.split('-'))
                    if start > end:
                        raise HTTPException(
                            status_code=400,
                            detail=f"页面范围错误: {start}-{end}，起始页不能大于结束页"
                        )
                    page_list.extend(range(start, end + 1))
                else:
                    # 处理单个页面
                    page_list.append(int(part))
            page_list = sorted(list(set(page_list)))  # 去重并排序
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="页面格式错误，请使用 '1,3,5' 或 '1-5' 格式"
            )
    
    # 创建请求对象
    request = PDFPageSelectionRequest(
        mode=mode,
        pages=page_list,
        filename_prefix=filename_prefix
    )
    
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
    description="返回API支持的文件格式列表"
)
async def get_supported_formats():
    """获取支持的文件格式"""
    return SuccessResponse(
        message="支持的文件格式",
        data={
            "input_formats": [".pdf"],
            "output_formats": [".pdf", ".zip"],
            "max_file_size": "100MB",
            "max_files_per_request": 50
        }
    )