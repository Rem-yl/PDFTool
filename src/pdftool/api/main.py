"""
FastAPI application for PDFTool web interface
"""

import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from ..core.pdf_operations import PDFOperations
from ..core.models import SplitOptions, MergeOptions, SplitMode
from ..core.exceptions import PDFToolError
from ..config.settings import settings
from ..utils.logging import setup_logging, get_logger
from .templates import get_html_template

# Setup logging
setup_logging()
logger = get_logger("api")

# Initialize FastAPI app
app = FastAPI(
    title=f"{settings.app_name} API",
    description="PDF操作工具API服务",
    version=settings.version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PDF operations
pdf_ops = PDFOperations(temp_dir=settings.temp_dir)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页面"""
    return get_html_template()


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.version
    }


@app.post("/merge")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    """合并多个PDF文件"""
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="需要至少2个PDF文件")
    
    temp_files = []
    try:
        # Save uploaded files temporarily
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"文件 {file.filename} 不是PDF格式")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                content = await file.read()
                tmp.write(content)
                temp_files.append(Path(tmp.name))
        
        # Merge PDFs
        options = MergeOptions()
        result = pdf_ops.merge_pdfs(temp_files, options)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        output_file = result.output_files[0]
        
        logger.info(f"Successfully merged {len(files)} PDFs")
        return FileResponse(
            output_file,
            media_type="application/pdf",
            filename="merged.pdf",
            background=lambda: pdf_ops.cleanup_temp_files([output_file] + temp_files)
        )
    
    except PDFToolError as e:
        pdf_ops.cleanup_temp_files(temp_files)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        pdf_ops.cleanup_temp_files(temp_files)
        logger.error(f"Merge operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"合并PDF时出错: {str(e)}")


@app.post("/split")
async def split_pdf(
    file: UploadFile = File(...),
    mode: str = Form(...),
    start_page: Optional[int] = Form(None),
    end_page: Optional[int] = Form(None)
):
    """拆分PDF文件"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="文件必须是PDF格式")
    
    temp_input = None
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_input = Path(tmp.name)
        
        # Setup split options
        split_mode = SplitMode.ALL_PAGES if mode == "all" else SplitMode.PAGE_RANGE
        options = SplitOptions(
            mode=split_mode,
            start_page=start_page,
            end_page=end_page,
            filename_prefix=Path(file.filename).stem
        )
        
        # Split PDF
        result = pdf_ops.split_pdf(temp_input, options)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        # Create ZIP file if multiple outputs
        if len(result.output_files) > 1:
            zip_file = pdf_ops.create_zip_archive(result.output_files)
            cleanup_files = [temp_input, zip_file] + result.output_files
            
            return FileResponse(
                zip_file,
                media_type="application/zip",
                filename="split_pages.zip",
                background=lambda: pdf_ops.cleanup_temp_files(cleanup_files)
            )
        else:
            output_file = result.output_files[0]
            cleanup_files = [temp_input, output_file]
            
            return FileResponse(
                output_file,
                media_type="application/pdf",
                filename=output_file.name,
                background=lambda: pdf_ops.cleanup_temp_files(cleanup_files)
            )
    
    except PDFToolError as e:
        if temp_input:
            pdf_ops.cleanup_temp_files([temp_input])
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if temp_input:
            pdf_ops.cleanup_temp_files([temp_input])
        logger.error(f"Split operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"拆分PDF时出错: {str(e)}")


@app.post("/info")
async def get_pdf_info(file: UploadFile = File(...)):
    """获取PDF文件信息"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="文件必须是PDF格式")
    
    temp_file = None
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file = Path(tmp.name)
        
        # Get PDF info
        info = pdf_ops.get_pdf_info(temp_file)
        
        return {
            "pages": info.pages,
            "title": info.title,
            "author": info.author,
            "creation_date": str(info.creation_date) if info.creation_date else None,
            "file_size": len(content)
        }
    
    except PDFToolError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Info operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取PDF信息时出错: {str(e)}")
    finally:
        if temp_file:
            pdf_ops.cleanup_temp_files([temp_file])


def main():
    """Main entry point for the PDFTool API server"""
    import uvicorn
    uvicorn.run(
        "pdftool.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=settings.api_workers
    )


if __name__ == "__main__":
    main()