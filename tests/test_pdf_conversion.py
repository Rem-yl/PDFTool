"""
PDF格式转换功能测试
特别关注PDF转EPUB时图像保留的问题
"""

import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

from pdftool.common.models import ConversionOptions, ConversionFormat, OperationResult
from pdftool.domains.document.operations.conversion import ConversionOperation


class TestPDFConversionImagePreservation:
    """测试PDF转换时图像保留功能"""

    @pytest.fixture
    def conversion_operation(self):
        """创建转换操作实例"""
        return ConversionOperation()

    @pytest.fixture
    def sample_pdf_with_images(self, temp_dir: Path) -> Path:
        """创建包含图像的测试PDF文件"""
        # 创建一个简单的PDF文件，包含一些图像数据
        from PyPDF2 import PdfWriter, PageObject

        pdf_path = temp_dir / "sample_with_images.pdf"
        writer = PdfWriter()

        # 创建多个页面模拟包含图像的PDF
        for i in range(3):
            page = PageObject.create_blank_page(width=595, height=842)  # A4大小
            writer.add_page(page)

        with open(pdf_path, "wb") as f:
            writer.write(f)

        return pdf_path

    @pytest.fixture
    def mock_paddle_ocr_with_images(self):
        """模拟PaddleOCR返回包含图像的结果"""
        # 创建模拟图像
        mock_image1 = Image.new('RGB', (100, 100), color='red')
        mock_image2 = Image.new('RGB', (150, 150), color='blue')

        # 模拟PaddleOCR的返回结果 - 修正结构以匹配实际代码
        mock_result1 = MagicMock()
        mock_result1.markdown = {
            'content': '# Page 1\n\nThis is the first page with an image.\n\n![Image 1](images/page1_img1.png)\n\nSome text after image.',
            'markdown_images': {
                'images/page1_img1.png': mock_image1
            }
        }

        mock_result2 = MagicMock()
        mock_result2.markdown = {
            'content': '# Page 2\n\nSecond page content.\n\n![Image 2](images/page2_img1.png)\n\nMore text content.',
            'markdown_images': {
                'images/page2_img1.png': mock_image2
            }
        }

        mock_result3 = MagicMock()
        mock_result3.markdown = {
            'content': '# Page 3\n\nThird page without images.\n\nJust text content.',
            'markdown_images': {}
        }

        mock_results = [mock_result1, mock_result2, mock_result3]

        return mock_results

    def test_markdown_conversion_preserves_images(self, conversion_operation, sample_pdf_with_images, mock_paddle_ocr_with_images, temp_dir):
        """测试PDF转Markdown时图像是否正确保存"""

        # Mock PaddleOCR pipeline
        with patch('pdftool.domains.document.operations.conversion.PPStructureV3') as mock_pipeline_class:
            mock_pipeline = MagicMock()
            mock_pipeline_class.return_value = mock_pipeline

            # 设置predict方法返回模拟结果
            mock_pipeline.predict.return_value = mock_paddle_ocr_with_images

            # 模拟concatenate_markdown_pages方法
            def mock_concatenate(markdown_list):
                contents = []
                for item in markdown_list:
                    contents.append(item['content'])
                return '\n\n---\n\n'.join(contents)

            mock_pipeline.concatenate_markdown_pages = mock_concatenate

            # Mock paddle device functions
            with patch('pdftool.domains.document.operations.conversion.paddle.device.get_device', return_value='gpu:0'), \
                 patch('pdftool.domains.document.operations.conversion.paddle.device.set_device'):

                # 执行转换
                options = ConversionOptions(
                    format=ConversionFormat.MARKDOWN,
                    output_file=temp_dir / "output.zip"
                )

                result = conversion_operation.execute(sample_pdf_with_images, options)

                # 验证转换成功
                assert result.success is True
                assert "successfully converted to Markdown" in result.message
                assert len(result.output_files) == 1
                assert result.output_files[0].suffix == '.zip'

                # 验证ZIP文件包含图像
                with zipfile.ZipFile(result.output_files[0], 'r') as zip_ref:
                    file_list = zip_ref.namelist()

                    # 检查markdown文件存在
                    markdown_files = [f for f in file_list if f.endswith('.md')]
                    assert len(markdown_files) == 1

                    # 检查图像文件存在
                    image_files = [f for f in file_list if f.startswith('images/') and f.endswith('.png')]
                    assert len(image_files) == 2  # 应该有两个图像文件
                    assert 'images/page1_img1.png' in file_list
                    assert 'images/page2_img1.png' in file_list

                    # 验证markdown内容包含图像引用
                    markdown_content = zip_ref.read(markdown_files[0]).decode('utf-8')
                    assert '![Image 1](images/page1_img1.png)' in markdown_content
                    assert '![Image 2](images/page2_img1.png)' in markdown_content

    def test_epub_conversion_includes_images(self, conversion_operation, sample_pdf_with_images, mock_paddle_ocr_with_images, temp_dir):
        """测试PDF转EPUB时图像是否被正确包含（这是需要修复的功能）"""

        # Mock pandoc availability check
        with patch.object(conversion_operation, '_check_pandoc_available', return_value=True):

            # Mock PaddleOCR pipeline for markdown conversion
            with patch('pdftool.domains.document.operations.conversion.PPStructureV3') as mock_pipeline_class:
                mock_pipeline = MagicMock()
                mock_pipeline_class.return_value = mock_pipeline
                mock_pipeline.predict.return_value = mock_paddle_ocr_with_images

                def mock_concatenate(markdown_list):
                    contents = []
                    for item in markdown_list:
                        contents.append(item.get('content', ''))
                    return '\n\n---\n\n'.join(contents)

                mock_pipeline.concatenate_markdown_pages = mock_concatenate

                # Mock paddle device functions
                with patch('pdftool.domains.document.operations.conversion.paddle.device.get_device', return_value='gpu:0'), \
                     patch('pdftool.domains.document.operations.conversion.paddle.device.set_device'):

                    # Mock subprocess.run for pandoc
                    mock_process_result = MagicMock()
                    mock_process_result.returncode = 0
                    mock_process_result.stderr = ""

                    def mock_pandoc_side_effect(cmd, **kwargs):
                        # 模拟pandoc创建EPUB文件
                        if '--to=epub' in cmd and '-o' in cmd:
                            output_file = cmd[cmd.index('-o') + 1]
                            Path(output_file).touch()  # 创建空文件模拟pandoc输出
                        return mock_process_result

                    with patch('pdftool.domains.document.operations.conversion.subprocess.run', side_effect=mock_pandoc_side_effect) as mock_subprocess:

                        # 执行EPUB转换
                        options = ConversionOptions(
                            format=ConversionFormat.EPUB,
                            output_file=temp_dir / "output.epub"
                        )

                        result = conversion_operation.execute(sample_pdf_with_images, options)

                        # 验证转换成功
                        assert result.success is True
                        assert "successfully converted to EPUB" in result.message
                        assert len(result.output_files) == 1
                        assert result.output_files[0].suffix == '.epub'

                        # 检查pandoc调用参数
                        assert mock_subprocess.called
                        pandoc_args = mock_subprocess.call_args[0][0]

                        # pandoc命令应该包含正确的参数
                        assert 'pandoc' in pandoc_args
                        assert '--from=markdown' in pandoc_args
                        assert '--to=epub' in pandoc_args
                        assert any('--metadata=title=' in arg for arg in pandoc_args)

    def test_epub_conversion_with_resource_dir_flag(self, conversion_operation, sample_pdf_with_images, mock_paddle_ocr_with_images, temp_dir):
        """测试修复后的EPUB转换应该使用--resource-path参数来包含图像"""

        # 这个测试验证修复后的功能：pandoc应该使用--resource-path参数来包含图像目录

        with patch.object(conversion_operation, '_check_pandoc_available', return_value=True):
            with patch('pdftool.domains.document.operations.conversion.PPStructureV3') as mock_pipeline_class:
                mock_pipeline = MagicMock()
                mock_pipeline_class.return_value = mock_pipeline
                mock_pipeline.predict.return_value = mock_paddle_ocr_with_images

                def mock_concatenate(markdown_list):
                    contents = []
                    for item in markdown_list:
                        contents.append(item.get('content', ''))
                    return '\n\n---\n\n'.join(contents)

                mock_pipeline.concatenate_markdown_pages = mock_concatenate

                with patch('pdftool.domains.document.operations.conversion.paddle.device.get_device', return_value='gpu:0'), \
                     patch('pdftool.domains.document.operations.conversion.paddle.device.set_device'):

                    mock_process_result = MagicMock()
                    mock_process_result.returncode = 0
                    mock_process_result.stderr = ""

                    def mock_pandoc_side_effect(cmd, **kwargs):
                        # 模拟pandoc创建EPUB文件
                        if '--to=epub' in cmd and '-o' in cmd:
                            output_file = cmd[cmd.index('-o') + 1]
                            Path(output_file).touch()  # 创建空文件模拟pandoc输出
                        return mock_process_result

                    with patch('pdftool.domains.document.operations.conversion.subprocess.run', side_effect=mock_pandoc_side_effect) as mock_subprocess:

                        options = ConversionOptions(
                            format=ConversionFormat.EPUB,
                            output_file=temp_dir / "output_with_images.epub"
                        )

                        result = conversion_operation.execute(sample_pdf_with_images, options)

                        assert result.success is True

                        # 验证pandoc调用包含了--resource-path参数（修复后应该有这个）
                        pandoc_args = mock_subprocess.call_args[0][0]

                        # 检查是否包含resource-path参数（这是修复的关键）
                        has_resource_path = any('--resource-path' in str(arg) for arg in pandoc_args)

                        # 现在应该有resource-path参数
                        assert has_resource_path, f"EPUB conversion should include --resource-path parameter to preserve images. Got args: {pandoc_args}"

    def test_txt_conversion_maintains_image_references(self, conversion_operation, sample_pdf_with_images, mock_paddle_ocr_with_images, temp_dir):
        """测试PDF转TXT时保持图像引用（虽然TXT不能包含图像，但应该保留引用信息）"""

        with patch.object(conversion_operation, '_check_pandoc_available', return_value=True):
            with patch('pdftool.domains.document.operations.conversion.PPStructureV3') as mock_pipeline_class:
                mock_pipeline = MagicMock()
                mock_pipeline_class.return_value = mock_pipeline
                mock_pipeline.predict.return_value = mock_paddle_ocr_with_images

                def mock_concatenate(markdown_list):
                    contents = []
                    for item in markdown_list:
                        contents.append(item.get('content', ''))
                    return '\n\n---\n\n'.join(contents)

                mock_pipeline.concatenate_markdown_pages = mock_concatenate

                with patch('pdftool.domains.document.operations.conversion.paddle.device.get_device', return_value='gpu:0'), \
                     patch('pdftool.domains.document.operations.conversion.paddle.device.set_device'):

                    # Mock pandoc calls - first for markdown to txt
                    mock_process_result = MagicMock()
                    mock_process_result.returncode = 0
                    mock_process_result.stderr = ""

                    def mock_pandoc_side_effect(cmd, **kwargs):
                        # 模拟pandoc将markdown转换为txt
                        if '--to=plain' in cmd:
                            # 模拟创建txt文件
                            output_file = cmd[cmd.index('-o') + 1]
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write("Page 1\n\nThis is the first page with an image.\n\n[Image 1: images/page1_img1.png]\n\nSome text after image.\n\nPage 2\n\nSecond page content.\n\n[Image 2: images/page2_img1.png]\n\nMore text content.\n\nPage 3\n\nThird page without images.\n\nJust text content.")
                        return mock_process_result

                    with patch('pdftool.domains.document.operations.conversion.subprocess.run', side_effect=mock_pandoc_side_effect) as mock_subprocess:

                        options = ConversionOptions(
                            format=ConversionFormat.TXT,
                            output_file=temp_dir / "output.txt"
                        )

                        result = conversion_operation.execute(sample_pdf_with_images, options)

                        assert result.success is True
                        assert "successfully converted to TXT" in result.message

                        # 验证TXT文件包含图像引用信息
                        txt_content = result.output_files[0].read_text(encoding='utf-8')
                        assert "Image 1" in txt_content
                        assert "Image 2" in txt_content

    def test_conversion_without_images(self, conversion_operation, sample_pdf_with_images, temp_dir):
        """测试没有图像的PDF转换"""

        # Mock没有图像的OCR结果
        mock_result_no_images = MagicMock()
        mock_result_no_images.markdown = {
            'content': '# Page 1\n\nText only content.',
            'markdown_images': {}
        }
        mock_results_no_images = [mock_result_no_images]

        with patch('pdftool.domains.document.operations.conversion.PPStructureV3') as mock_pipeline_class:
            mock_pipeline = MagicMock()
            mock_pipeline_class.return_value = mock_pipeline
            mock_pipeline.predict.return_value = mock_results_no_images

            def mock_concatenate(markdown_list):
                return markdown_list[0].get('content', '')

            mock_pipeline.concatenate_markdown_pages = mock_concatenate

            with patch('pdftool.domains.document.operations.conversion.paddle.device.get_device', return_value='gpu:0'), \
                 patch('pdftool.domains.document.operations.conversion.paddle.device.set_device'):

                options = ConversionOptions(
                    format=ConversionFormat.MARKDOWN,
                    output_file=temp_dir / "output_no_images.zip"
                )

                result = conversion_operation.execute(sample_pdf_with_images, options)

                assert result.success is True

                # 验证ZIP文件只包含markdown文件，没有图像
                with zipfile.ZipFile(result.output_files[0], 'r') as zip_ref:
                    file_list = zip_ref.namelist()

                    # 只应该有markdown文件
                    markdown_files = [f for f in file_list if f.endswith('.md')]
                    assert len(markdown_files) == 1

                    # 不应该有图像文件
                    image_files = [f for f in file_list if f.startswith('images/')]
                    assert len(image_files) == 0

    def test_error_handling_invalid_format(self, conversion_operation, sample_pdf_with_images):
        """测试无效格式的错误处理"""

        options = ConversionOptions(format=ConversionFormat.TXT)  # 使用有效格式，然后手动设置无效值进行测试
        options.format = "invalid_format"  # 手动设置无效格式来测试错误处理
        result = conversion_operation.execute(sample_pdf_with_images, options)

        assert result.success is False
        assert "Unsupported format" in result.message

    def test_pandoc_not_available_error(self, conversion_operation, sample_pdf_with_images):
        """测试pandoc不可用时的错误处理"""

        with patch.object(conversion_operation, '_check_pandoc_available', return_value=False):

            options = ConversionOptions(format=ConversionFormat.EPUB)
            result = conversion_operation.execute(sample_pdf_with_images, options)

            assert result.success is False
            assert "pandoc" in result.message.lower()
            assert "requires pandoc to be installed" in result.message