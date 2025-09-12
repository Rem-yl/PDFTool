"""
Core PDF operations module
"""

import logging
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional, Union
from uuid import uuid4

import PyPDF2

from .exceptions import PDFProcessingError, PDFValidationError, PDFFileNotFoundError
from .models import PDFInfo, SplitOptions, MergeOptions, OperationResult, SplitMode


logger = logging.getLogger(__name__)


class PDFOperations:
    """Core class for PDF operations"""
    
    def __init__(self, temp_dir: Optional[Path] = None):
        """
        Initialize PDF operations
        
        Args:
            temp_dir: Directory for temporary files. If None, uses system temp
        """
        self.temp_dir = temp_dir or Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    def validate_pdf_file(self, file_path: Path) -> None:
        """Validate that a file is a valid PDF"""
        if not file_path.exists():
            raise PDFFileNotFoundError(f"PDF file not found: {file_path}")
        
        if file_path.suffix.lower() != '.pdf':
            raise PDFValidationError(f"File is not a PDF: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                PyPDF2.PdfReader(f)
        except Exception as e:
            raise PDFValidationError(f"Invalid PDF file: {file_path}. Error: {str(e)}")
    
    def get_pdf_info(self, file_path: Path) -> PDFInfo:
        """Get information about a PDF file"""
        self.validate_pdf_file(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                info = PDFInfo(
                    pages=len(reader.pages),
                    file_path=file_path,
                    file_size=file_path.stat().st_size
                )
                
                if reader.metadata:
                    info.title = reader.metadata.title
                    info.author = reader.metadata.author
                    info.creation_date = reader.metadata.creation_date
                
                return info
                
        except Exception as e:
            raise PDFProcessingError(f"Failed to read PDF info: {str(e)}")
    
    def merge_pdfs(self, input_files: List[Path], options: Optional[MergeOptions] = None) -> OperationResult:
        """Merge multiple PDF files into one"""
        if len(input_files) < 2:
            raise PDFValidationError("At least 2 PDF files are required for merging")
        
        for file_path in input_files:
            self.validate_pdf_file(file_path)
        
        options = options or MergeOptions()
        output_file = options.output_file or self.temp_dir / f"merged_{uuid4().hex}.pdf"
        
        try:
            merger = PyPDF2.PdfMerger()
            
            for file_path in input_files:
                merger.append(str(file_path))
            
            with open(output_file, 'wb') as f:
                merger.write(f)
            
            merger.close()
            
            logger.info(f"Successfully merged {len(input_files)} PDFs into {output_file}")
            return OperationResult(
                success=True,
                message=f"Successfully merged {len(input_files)} PDF files",
                output_files=[output_file]
            )
            
        except Exception as e:
            raise PDFProcessingError(f"Failed to merge PDFs: {str(e)}")
    
    def split_pdf(self, input_file: Path, options: SplitOptions) -> OperationResult:
        """Split a PDF file according to specified options"""
        self.validate_pdf_file(input_file)
        
        output_dir = options.output_dir or self.temp_dir / f"split_{uuid4().hex}"
        output_dir.mkdir(exist_ok=True)
        
        try:
            with open(input_file, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                total_pages = len(reader.pages)
                output_files = []
                
                if options.mode == SplitMode.ALL_PAGES:
                    for page_num in range(total_pages):
                        writer = PyPDF2.PdfWriter()
                        writer.add_page(reader.pages[page_num])
                        
                        filename = f"{options.filename_prefix or input_file.stem}_page_{page_num + 1}.pdf"
                        output_file = output_dir / filename
                        
                        with open(output_file, 'wb') as out_f:
                            writer.write(out_f)
                        
                        output_files.append(output_file)
                
                elif options.mode == SplitMode.PAGE_RANGE:
                    start = (options.start_page or 1) - 1
                    end = options.end_page or total_pages
                    
                    if start < 0 or end > total_pages or start >= end:
                        raise PDFValidationError("Invalid page range")
                    
                    writer = PyPDF2.PdfWriter()
                    for page_num in range(start, end):
                        writer.add_page(reader.pages[page_num])
                    
                    filename = f"{options.filename_prefix or input_file.stem}_pages_{start + 1}-{end}.pdf"
                    output_file = output_dir / filename
                    
                    with open(output_file, 'wb') as out_f:
                        writer.write(out_f)
                    
                    output_files.append(output_file)
                
                logger.info(f"Successfully split PDF into {len(output_files)} files")
                return OperationResult(
                    success=True,
                    message=f"Successfully split PDF into {len(output_files)} files",
                    output_files=output_files
                )
                
        except Exception as e:
            raise PDFProcessingError(f"Failed to split PDF: {str(e)}")
    
    def create_zip_archive(self, files: List[Path], output_path: Optional[Path] = None) -> Path:
        """Create a ZIP archive from a list of files"""
        output_path = output_path or self.temp_dir / f"archive_{uuid4().hex}.zip"
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in files:
                    zf.write(file_path, file_path.name)
            
            return output_path
            
        except Exception as e:
            raise PDFProcessingError(f"Failed to create ZIP archive: {str(e)}")
    
    def cleanup_temp_files(self, files: List[Path]) -> None:
        """Clean up temporary files"""
        for file_path in files:
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {str(e)}")