"""
PDF操作API路由
"""

from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Depends, Form, HTTPException
from fastapi.responses import FileResponse

from ..dependencies import get_pdf_operations, validate_file_size, validate_file_extension
from ..services.pdf_service import PDFService
from ..schemas.requests import PDFSplitRequest, PDFMergeRequest, SplitModeEnum
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