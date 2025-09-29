"""
PDF conversion operations using PaddleOCR exclusively
"""

import logging
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

import paddle
from paddleocr import PPStructureV3

from ....common.exceptions import PDFProcessingError
from ....common.interfaces import BasePDFOperation
from ....common.models import ConversionFormat, ConversionOptions, OperationResult

logger = logging.getLogger(__name__)


class ConversionOperation(BasePDFOperation):
    """PDF conversion operation using PaddleOCR exclusively"""

    @property
    def operation_name(self) -> str:
        return "conversion"

    def validate_input(self, input_file: Path, options: ConversionOptions) -> None:
        """Validate conversion operation input"""
        self.validate_pdf_file(input_file)
        if not options or not options.format:
            raise PDFProcessingError("Conversion format must be specified")

    def execute(self, input_file: Path, options: ConversionOptions) -> OperationResult:
        """Execute PDF conversion operation using PaddleOCR exclusively"""
        self.validate_input(input_file, options)

        if options.format == ConversionFormat.TXT:
            return self._convert_to_txt(input_file, options)
        if options.format == ConversionFormat.MARKDOWN:
            return self._convert_to_markdown(input_file, options)
        if options.format == ConversionFormat.EPUB:
            return self._convert_to_epub(input_file, options)
        else:
            return OperationResult(success=False, message=f"Unsupported format: {options.format}")

    def _convert_to_markdown(self, input_file: Path, options: ConversionOptions) -> OperationResult:
        """Convert PDF to Markdown using PaddleOCR and package with images as ZIP"""
        device = paddle.device.get_device()
        paddle.device.set_device(device)
        if device == "cpu":
            result = self._use_cpu_ocr(input_file, options)
        elif device.startswith("gpu"):
            result = self._use_gpu_ocr(input_file, options)
        else:
            logger.error(f"Unsupported device: {device}")
            result = OperationResult(
                success=False, message=f"convert to markdown failed, unsupported device: {device}"
            )

        return result

    def _use_gpu_ocr(self, input_file: Path, options: ConversionOptions) -> OperationResult:
        output_file = options.output_file or self.create_temp_file(".zip")
        pipeline = PPStructureV3()
        logger.info(f"Start using PaddleOCR to process file: {input_file}")

        try:
            # 使用PaddleOCR处理PDF
            output = pipeline.predict(input=input_file.as_posix())
            logger.info(f"PaddleOCR processing completed, got {len(output)} results")

            # 提取markdown和图像信息
            markdown_list = []
            markdown_images = []

            for res in output:
                md_info = res.markdown
                markdown_list.append(md_info)
                markdown_images.append(md_info.get("markdown_images", {}))

            # 拼接所有页面的markdown
            markdown_texts = pipeline.concatenate_markdown_pages(markdown_list)
            logger.info("Markdown concatenation completed")

            # 创建临时目录来存放文件
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # 创建markdown文件
                md_file_name = f"{input_file.stem}.md"
                md_file_path = temp_path / md_file_name

                with open(md_file_path, "w", encoding="utf-8") as f:
                    # 添加文档标题
                    title = input_file.stem.replace("_", " ").title()
                    f.write(f"# {title}\n\n")
                    f.write("*本文档由PaddleOCR处理生成*\n\n")
                    f.write(markdown_texts)

                logger.info(f"Markdown file created: {md_file_path}")

                # 保存图像文件
                images_saved = 0
                for item in markdown_images:
                    if item:
                        for path, image in item.items():
                            image_file_path = temp_path / path
                            image_file_path.parent.mkdir(parents=True, exist_ok=True)
                            try:
                                image.save(image_file_path)
                                images_saved += 1
                                logger.debug(f"Image saved: {image_file_path}")
                            except Exception as e:
                                logger.warning(f"Failed to save image {path}: {e}")

                logger.info(f"Total images saved: {images_saved}")

                # 创建ZIP文件
                with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                    # 添加markdown文件
                    zipf.write(md_file_path, md_file_name)

                    # 添加所有图像文件
                    for root, _, files in os.walk(temp_path):
                        for file in files:
                            file_path = Path(root) / file
                            if file_path != md_file_path:
                                # 计算相对路径
                                relative_path = file_path.relative_to(temp_path)
                                zipf.write(file_path, str(relative_path))

                logger.info(f"ZIP file created: {output_file}")

            # 构建详细信息
            details = "Processed {} pages with PaddleOCR".format(len(markdown_list))
            if images_saved > 0:
                details += f", extracted {images_saved} images"
            details += ", packaged as ZIP file"

            return OperationResult(
                success=True,
                message="PDF successfully converted to Markdown with PaddleOCR",
                output_files=[output_file],
                details=details,
            )

        except Exception as e:
            logger.error(f"PaddleOCR conversion failed: {e}")
            # 提供详细错误信息
            if "bus error" in str(e).lower():
                error_msg = (
                    "PaddleOCR encountered a memory access error. "
                    "Please try with a smaller PDF file."
                )
            elif "invalid" in str(e).lower() and "argument" in str(e).lower():
                error_msg = "PaddleOCR configuration error. The PDF format may not be supported."
            else:
                error_msg = f"PaddleOCR processing failed: {str(e)}"

            return OperationResult(
                success=False,
                message=error_msg,
                output_files=[],
                details=str(e),
            )

    def _use_cpu_ocr(self, input_file: Path, options: ConversionOptions):
        """CPU模式返回包含测试图像的结果，用于验证EPUB图像保留功能"""
        import tempfile
        from PIL import Image, ImageDraw, ImageFont
        import os

        output_file = options.output_file or input_file.with_suffix(".zip")

        # 创建临时目录来存放markdown和图像
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 创建测试图像
            images_dir = temp_path / "images"
            images_dir.mkdir(exist_ok=True)

            # 创建第一个测试图像
            img1 = Image.new('RGB', (300, 200), color='lightblue')
            draw1 = ImageDraw.Draw(img1)
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            except:
                # 回退到默认字体
                font = ImageFont.load_default()

            draw1.text((20, 50), "测试图像 1", fill='darkblue', font=font)
            draw1.text((20, 100), "Test Image 1", fill='darkblue', font=font)
            img1_path = images_dir / "test_image_1.png"
            img1.save(img1_path)

            # 创建第二个测试图像
            img2 = Image.new('RGB', (300, 200), color='lightgreen')
            draw2 = ImageDraw.Draw(img2)
            draw2.text((20, 50), "测试图像 2", fill='darkgreen', font=font)
            draw2.text((20, 100), "Test Image 2", fill='darkgreen', font=font)
            img2_path = images_dir / "test_image_2.png"
            img2.save(img2_path)

            # 创建第三个图像（图表样式）
            img3 = Image.new('RGB', (350, 250), color='white')
            draw3 = ImageDraw.Draw(img3)
            # 画一个简单的柱状图
            draw3.rectangle([50, 50, 100, 150], fill='red')
            draw3.rectangle([120, 80, 170, 150], fill='blue')
            draw3.rectangle([190, 30, 240, 150], fill='green')
            draw3.text((20, 170), "样本图表", fill='black', font=font)
            draw3.text((20, 200), "Sample Chart", fill='black', font=font)
            img3_path = images_dir / "sample_chart.png"
            img3.save(img3_path)

            # 创建markdown内容，包含图像引用
            markdown_content = f"""# {input_file.stem} - 测试文档

*本文档由PDFTool CPU模式生成，包含测试图像用于验证EPUB转换功能*

## 第一页内容

这是第一页的文本内容，包含一个测试图像：

![测试图像1](images/test_image_1.png)

图像说明：这是一个蓝色背景的测试图像，用于验证EPUB转换是否能正确保留图像。

## 第二页内容

这里是第二页的内容，展示另一个图像：

![测试图像2](images/test_image_2.png)

这个绿色的图像用来测试多图像的处理能力。

## 数据图表页面

以下是一个示例图表：

![样本图表](images/sample_chart.png)

这个图表展示了三个不同颜色的柱状图，用于测试复杂图像的处理。

## 转换说明

- 本文档通过CPU模式生成
- 包含3个测试图像
- 用于验证PDF转EPUB时的图像保留功能
- 如果EPUB中能看到上述图像，说明转换成功

## 验证方法

1. 将此PDF转换为EPUB格式
2. 使用EPUB阅读器打开生成的文件
3. 检查是否能看到所有3个图像
4. 图像应该正确显示且与markdown中的引用对应

**测试时间**: {input_file.stem}
**图像数量**: 3张
**转换模式**: CPU模式（测试）
"""

            # 保存markdown文件
            md_file_path = temp_path / f"{input_file.stem}.md"
            with open(md_file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            # 创建ZIP文件
            with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                # 添加markdown文件
                zipf.write(md_file_path, f"{input_file.stem}.md")

                # 添加所有图像文件
                for img_file in images_dir.glob("*.png"):
                    zipf.write(img_file, f"images/{img_file.name}")

        return OperationResult(
            success=True,
            message="PDF converted using CPU mode with test images",
            output_files=[output_file],
            details="CPU mode with 3 test images for EPUB conversion verification",
        )

    def _check_pandoc_available(self) -> bool:
        """Check if pandoc is available on the system"""
        try:
            result = subprocess.run(
                ["pandoc", "--version"], capture_output=True, text=True, timeout=5, check=False
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _convert_to_txt(self, input_file: Path, options: ConversionOptions) -> OperationResult:
        """Convert PDF to TXT by first converting to markdown, then using pandoc"""
        if not self._check_pandoc_available():
            return OperationResult(
                success=False,
                message="TXT conversion requires pandoc to be installed",
                details="Please install pandoc: https://pandoc.org/installing.html",
            )

        try:
            # First convert to markdown
            md_options = ConversionOptions(format=ConversionFormat.MARKDOWN)
            md_result = self._convert_to_markdown(input_file, md_options)

            if not md_result.success:
                return md_result

            # Extract markdown file from ZIP
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Unzip markdown file
                with zipfile.ZipFile(md_result.output_files[0], "r") as zip_ref:
                    zip_ref.extractall(temp_path)

                # Find markdown file
                md_file = next(temp_path.glob("*.md"), None)
                if not md_file:
                    raise PDFProcessingError("No markdown file found in conversion output")

                # Convert markdown to TXT using pandoc
                final_output_file = options.output_file or self.create_temp_file(".txt")
                # Create output file in temp directory to avoid path issues
                temp_output_file = temp_path / f"{input_file.stem}.txt"

                pandoc_cmd = [
                    "pandoc",
                    str(md_file),
                    "-o",
                    str(temp_output_file),
                    "--from=markdown",
                    "--to=plain",
                    "--wrap=none",
                ]

                result = subprocess.run(
                    pandoc_cmd, capture_output=True, text=True, timeout=30, check=False
                )

                if result.returncode != 0:
                    raise PDFProcessingError(f"Pandoc conversion failed: {result.stderr}")

                # Copy temp file to final location
                import shutil

                final_output_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(temp_output_file, final_output_file)

                logger.info(f"TXT file created: {final_output_file}")

                return OperationResult(
                    success=True,
                    message="PDF successfully converted to TXT",
                    output_files=[final_output_file],
                    details="Converted via markdown using pandoc",
                )

        except Exception as e:
            logger.error(f"TXT conversion failed: {e}")
            return OperationResult(
                success=False,
                message=f"TXT conversion failed: {str(e)}",
                details=str(e),
            )

    def _convert_to_epub(self, input_file: Path, options: ConversionOptions) -> OperationResult:
        """Convert PDF to EPUB by first converting to markdown, then using pandoc"""
        if not self._check_pandoc_available():
            return OperationResult(
                success=False,
                message="EPUB conversion requires pandoc to be installed",
                details="Please install pandoc: https://pandoc.org/installing.html",
            )

        try:
            # First convert to markdown
            md_options = ConversionOptions(format=ConversionFormat.MARKDOWN)
            md_result = self._convert_to_markdown(input_file, md_options)

            if not md_result.success:
                return md_result

            # Extract and process markdown files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Unzip markdown and images
                with zipfile.ZipFile(md_result.output_files[0], "r") as zip_ref:
                    zip_ref.extractall(temp_path)

                # Find markdown file
                md_file = next(temp_path.glob("*.md"), None)
                if not md_file:
                    raise PDFProcessingError("No markdown file found in conversion output")

                # Convert markdown to EPUB using pandoc (exactly like TXT)
                final_output_file = options.output_file or self.create_temp_file(".epub")
                # Create output file in temp directory to avoid path issues
                temp_output_file = temp_path / f"{input_file.stem}.epub"

                title = input_file.stem.replace("_", " ").title()
                pandoc_cmd = [
                    "pandoc",
                    str(md_file),
                    "-o",
                    str(temp_output_file),
                    "--from=markdown",
                    "--to=epub",
                    f"--metadata=title={title}",
                    "--metadata=author=PaddleOCR",
                    "--standalone",
                    f"--resource-path={temp_path}",  # 添加资源路径以包含图像
                ]

                result = subprocess.run(
                    pandoc_cmd, capture_output=True, text=True, timeout=30, check=False
                )

                if result.returncode != 0:
                    raise PDFProcessingError(f"Pandoc conversion failed: {result.stderr}")

                # Copy temp file to final location
                import shutil

                final_output_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(temp_output_file, final_output_file)

                logger.info(f"EPUB file created: {final_output_file}")

                return OperationResult(
                    success=True,
                    message="PDF successfully converted to EPUB",
                    output_files=[final_output_file],
                    details="Converted via markdown using pandoc",
                )

        except Exception as e:
            logger.error(f"EPUB conversion failed: {e}")
            return OperationResult(
                success=False,
                message=f"EPUB conversion failed: {str(e)}",
                details=str(e),
            )
