"""
Tests for PDF operations
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from pdftool.core.pdf_operations import PDFOperations
from pdftool.core.models import SplitOptions, MergeOptions, SplitMode
from pdftool.core.exceptions import PDFValidationError, PDFProcessingError


class TestPDFOperations:
    """Test cases for PDFOperations class"""
    
    @pytest.fixture
    def pdf_ops(self):
        """Create PDFOperations instance for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield PDFOperations(temp_dir=Path(temp_dir))
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Create a sample PDF file for testing"""
        # This would normally create a real PDF file
        # For testing, we'll mock the PDF operations
        return Path("sample.pdf")
    
    def test_validate_pdf_file_not_found(self, pdf_ops):
        """Test validation fails for non-existent file"""
        non_existent_file = Path("non_existent.pdf")
        
        with pytest.raises(PDFValidationError, match="PDF file not found"):
            pdf_ops.validate_pdf_file(non_existent_file)
    
    def test_validate_pdf_file_wrong_extension(self, pdf_ops):
        """Test validation fails for non-PDF file"""
        # Create a temporary file with wrong extension
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            with pytest.raises(PDFValidationError, match="File is not a PDF"):
                pdf_ops.validate_pdf_file(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
    
    @patch('pdftool.core.pdf_operations.PyPDF2.PdfReader')
    def test_get_pdf_info_success(self, mock_reader, pdf_ops):
        """Test successful PDF info extraction"""
        # Mock PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock(), Mock()]  # 2 pages
        mock_reader_instance.metadata = Mock()
        mock_reader_instance.metadata.title = "Test PDF"
        mock_reader_instance.metadata.author = "Test Author"
        mock_reader_instance.metadata.creation_date = None
        mock_reader.return_value = mock_reader_instance
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"dummy pdf content")
        
        try:
            info = pdf_ops.get_pdf_info(tmp_path)
            
            assert info.pages == 2
            assert info.title == "Test PDF"
            assert info.author == "Test Author"
            assert info.file_path == tmp_path
            assert info.file_size > 0
        finally:
            tmp_path.unlink(missing_ok=True)
    
    @patch('pdftool.core.pdf_operations.PyPDF2.PdfMerger')
    def test_merge_pdfs_success(self, mock_merger, pdf_ops):
        """Test successful PDF merging"""
        # Create temporary PDF files
        pdf_files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(b"dummy pdf content")
                pdf_files.append(tmp_path)
        
        try:
            # Mock merger
            mock_merger_instance = Mock()
            mock_merger.return_value = mock_merger_instance
            
            options = MergeOptions()
            result = pdf_ops.merge_pdfs(pdf_files, options)
            
            assert result.success
            assert len(result.output_files) == 1
            assert "merged" in result.message.lower()
            
            # Verify merger was called correctly
            mock_merger_instance.append.assert_called()
            mock_merger_instance.write.assert_called()
            mock_merger_instance.close.assert_called()
            
        finally:
            for pdf_file in pdf_files:
                pdf_file.unlink(missing_ok=True)
    
    def test_merge_pdfs_insufficient_files(self, pdf_ops):
        """Test merge fails with insufficient files"""
        with pytest.raises(PDFValidationError, match="At least 2 PDF files are required"):
            pdf_ops.merge_pdfs([Path("single.pdf")])
    
    @patch('pdftool.core.pdf_operations.PyPDF2.PdfReader')
    @patch('pdftool.core.pdf_operations.PyPDF2.PdfWriter')
    def test_split_pdf_all_pages(self, mock_writer, mock_reader, pdf_ops):
        """Test PDF splitting all pages"""
        # Mock PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock(), Mock(), Mock()]  # 3 pages
        mock_reader.return_value = mock_reader_instance
        
        # Mock PDF writer
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"dummy pdf content")
        
        try:
            options = SplitOptions(mode=SplitMode.ALL_PAGES)
            result = pdf_ops.split_pdf(tmp_path, options)
            
            assert result.success
            assert len(result.output_files) == 3
            assert "split" in result.message.lower()
            
        finally:
            tmp_path.unlink(missing_ok=True)
    
    @patch('pdftool.core.pdf_operations.PyPDF2.PdfReader')
    @patch('pdftool.core.pdf_operations.PyPDF2.PdfWriter')
    def test_split_pdf_page_range(self, mock_writer, mock_reader, pdf_ops):
        """Test PDF splitting by page range"""
        # Mock PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock() for _ in range(5)]  # 5 pages
        mock_reader.return_value = mock_reader_instance
        
        # Mock PDF writer
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"dummy pdf content")
        
        try:
            options = SplitOptions(
                mode=SplitMode.PAGE_RANGE,
                start_page=2,
                end_page=4
            )
            result = pdf_ops.split_pdf(tmp_path, options)
            
            assert result.success
            assert len(result.output_files) == 1
            
        finally:
            tmp_path.unlink(missing_ok=True)
    
    def test_split_pdf_invalid_range(self, pdf_ops):
        """Test split fails with invalid page range"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"dummy pdf content")
        
        try:
            with patch('pdftool.core.pdf_operations.PyPDF2.PdfReader') as mock_reader:
                mock_reader_instance = Mock()
                mock_reader_instance.pages = [Mock(), Mock()]  # 2 pages
                mock_reader.return_value = mock_reader_instance
                
                options = SplitOptions(
                    mode=SplitMode.PAGE_RANGE,
                    start_page=3,  # Invalid: beyond available pages
                    end_page=5
                )
                
                with pytest.raises(PDFValidationError, match="Invalid page range"):
                    pdf_ops.split_pdf(tmp_path, options)
                    
        finally:
            tmp_path.unlink(missing_ok=True)
    
    def test_create_zip_archive(self, pdf_ops):
        """Test ZIP archive creation"""
        # Create temporary files
        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix=f"_file_{i}.pdf", delete=False) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(f"content {i}".encode())
                temp_files.append(tmp_path)
        
        try:
            zip_path = pdf_ops.create_zip_archive(temp_files)
            
            assert zip_path.exists()
            assert zip_path.suffix == ".zip"
            
        finally:
            for temp_file in temp_files:
                temp_file.unlink(missing_ok=True)
            if zip_path.exists():
                zip_path.unlink()
    
    def test_cleanup_temp_files(self, pdf_ops):
        """Test temporary file cleanup"""
        # Create temporary files
        temp_files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                temp_files.append(Path(tmp.name))
        
        # Verify files exist
        for temp_file in temp_files:
            assert temp_file.exists()
        
        # Cleanup
        pdf_ops.cleanup_temp_files(temp_files)
        
        # Verify files are gone
        for temp_file in temp_files:
            assert not temp_file.exists()