"""
Tests for PDF operations
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pdftool.core.exceptions import (
    PDFFileNotFoundError,
    PDFProcessingError,
    PDFValidationError,
)
from pdftool.core.models import (
    MergeOptions,
    SplitMode,
    SplitOptions,
    WatermarkOptions,
    WatermarkPosition,
    WatermarkType,
)
from pdftool.core.pdf_operations import PDFOperations


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

        with pytest.raises(PDFFileNotFoundError, match="PDF file not found"):
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

    @patch("pdftool.core.pdf_operations.PyPDF2.PdfReader")
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

    @patch("pdftool.core.pdf_operations.PyPDF2.PdfMerger")
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

    @patch("pdftool.core.pdf_operations.PyPDF2.PdfReader")
    @patch("pdftool.core.pdf_operations.PyPDF2.PdfWriter")
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

    @patch("pdftool.core.pdf_operations.PyPDF2.PdfReader")
    @patch("pdftool.core.pdf_operations.PyPDF2.PdfWriter")
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
            options = SplitOptions(mode=SplitMode.PAGE_RANGE, start_page=2, end_page=4)
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
            with patch("pdftool.core.pdf_operations.PyPDF2.PdfReader") as mock_reader:
                mock_reader_instance = Mock()
                mock_reader_instance.pages = [Mock(), Mock()]  # 2 pages
                mock_reader.return_value = mock_reader_instance

                options = SplitOptions(
                    mode=SplitMode.PAGE_RANGE,
                    start_page=3,  # Invalid: beyond available pages
                    end_page=5,
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

    @patch("pdftool.core.pdf_operations.PyPDF2.PdfReader")
    @patch("pdftool.core.pdf_operations.PyPDF2.PdfWriter")
    @patch("pdftool.core.pdf_operations.canvas.Canvas")
    def test_add_text_watermark_success(self, mock_canvas, mock_writer, mock_reader, pdf_ops):
        """Test successful text watermark addition"""
        # Mock PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock(), Mock()]  # 2 pages
        mock_reader.return_value = mock_reader_instance

        # Mock PDF writer
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance

        # Mock canvas
        mock_canvas_instance = Mock()
        mock_canvas.return_value = mock_canvas_instance
        mock_canvas_instance.stringWidth.return_value = 100

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"dummy pdf content")

        try:
            # Create watermark options
            options = WatermarkOptions(
                watermark_type=WatermarkType.TEXT,
                position=WatermarkPosition.CENTER,
                opacity=0.5,
                text="Test Watermark",
                font_size=36,
                font_color="#FF0000",
            )

            result = pdf_ops.add_watermark(tmp_path, options)

            assert result.success
            assert len(result.output_files) == 1
            assert "水印" in result.message

            # Verify canvas methods were called
            mock_canvas_instance.setFillAlpha.assert_called_with(0.5)
            mock_canvas_instance.setFont.assert_called()
            mock_canvas_instance.drawString.assert_called()

        finally:
            tmp_path.unlink(missing_ok=True)

    @patch("pdftool.core.pdf_operations.PyPDF2.PdfReader")
    @patch("pdftool.core.pdf_operations.PyPDF2.PdfWriter")
    @patch("pdftool.core.pdf_operations.canvas.Canvas")
    @patch("pdftool.core.pdf_operations.Image.open")
    def test_add_image_watermark_success(
        self, mock_image_open, mock_canvas, mock_writer, mock_reader, pdf_ops
    ):
        """Test successful image watermark addition"""
        # Mock PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock()]  # 1 page
        mock_reader.return_value = mock_reader_instance

        # Mock PDF writer
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance

        # Mock canvas
        mock_canvas_instance = Mock()
        mock_canvas.return_value = mock_canvas_instance

        # Mock image
        mock_image = Mock()
        mock_image.size = (100, 50)
        mock_image_open.return_value = mock_image

        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
            pdf_path = Path(tmp_pdf.name)
            tmp_pdf.write(b"dummy pdf content")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
            img_path = Path(tmp_img.name)
            tmp_img.write(b"dummy image content")

        try:
            # Create watermark options
            options = WatermarkOptions(
                watermark_type=WatermarkType.IMAGE,
                position=WatermarkPosition.BOTTOM_RIGHT,
                opacity=0.3,
                image_path=img_path,
                image_scale=150.0,
            )

            result = pdf_ops.add_watermark(pdf_path, options)

            assert result.success
            assert len(result.output_files) == 1
            assert "水印" in result.message

            # Verify image methods were called
            mock_image_open.assert_called_with(img_path)
            mock_canvas_instance.drawImage.assert_called()

        finally:
            pdf_path.unlink(missing_ok=True)
            img_path.unlink(missing_ok=True)

    def test_add_watermark_invalid_file(self, pdf_ops):
        """Test watermark fails with invalid file"""
        non_existent_file = Path("non_existent.pdf")

        options = WatermarkOptions(
            watermark_type=WatermarkType.TEXT,
            position=WatermarkPosition.CENTER,
            opacity=0.5,
            text="Test",
        )

        with pytest.raises(PDFFileNotFoundError, match="PDF file not found"):
            pdf_ops.add_watermark(non_existent_file, options)

    @patch("pdftool.core.pdf_operations.PyPDF2.PdfReader")
    def test_add_watermark_missing_text(self, mock_reader, pdf_ops):
        """Test watermark fails with missing text for text watermark"""
        # Mock PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock()]
        mock_reader.return_value = mock_reader_instance

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"dummy pdf content")

        try:
            # Create watermark options without text
            options = WatermarkOptions(
                watermark_type=WatermarkType.TEXT,
                position=WatermarkPosition.CENTER,
                opacity=0.5,
                text=None,  # Missing text
            )

            with pytest.raises(PDFProcessingError, match="文本水印需要提供文本内容"):
                pdf_ops.add_watermark(tmp_path, options)

        finally:
            tmp_path.unlink(missing_ok=True)

    @patch("pdftool.core.pdf_operations.PyPDF2.PdfReader")
    def test_add_watermark_missing_image(self, mock_reader, pdf_ops):
        """Test watermark fails with missing image for image watermark"""
        # Mock PDF reader
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock()]
        mock_reader.return_value = mock_reader_instance

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(b"dummy pdf content")

        try:
            # Create watermark options without image
            options = WatermarkOptions(
                watermark_type=WatermarkType.IMAGE,
                position=WatermarkPosition.CENTER,
                opacity=0.5,
                image_path=None,  # Missing image
            )

            with pytest.raises(PDFProcessingError, match="图片水印需要提供有效的图片文件"):
                pdf_ops.add_watermark(tmp_path, options)

        finally:
            tmp_path.unlink(missing_ok=True)
