"""
PDF conversion operations using PaddleOCR exclusively
"""

import logging
from pathlib import Path

import paddle

from ....common.exceptions import PDFProcessingError
from ....common.interfaces import BasePDFOperation
from ....common.models import ConversionFormat, ConversionOptions, OperationResult

logger = logging.getLogger(__name__)

# Try to import PaddleOCR dependencies, fall back gracefully if not available
try:
    from paddleocr import PPStructureV3

    logger.info("PaddleOCR dependencies loaded successfully")
except (ImportError, OSError) as e:
    raise ValueError(f"PaddleOCR dependencies not available: {e}")


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

        try:
            if options.format == ConversionFormat.TXT:
                raise PDFProcessingError("TXT format not be implemented.")
            elif options.format == ConversionFormat.MARKDOWN:
                return self._convert_to_markdown(input_file, options)
            elif options.format == ConversionFormat.EPUB:
                raise PDFProcessingError("EPUB format not be implemented.")
            else:
                raise PDFProcessingError(f"Unsupported format: {options.format}")

        except Exception as e:
            logger.error(f"PaddleOCR conversion failed: {str(e)}")
            raise PDFProcessingError(f"Conversion failed: {str(e)}")

    def _convert_to_markdown(self, input_file: Path, options: ConversionOptions) -> OperationResult:
        """Convert PDF to Markdown using PaddleOCR and package with images as ZIP"""
        import os
        import tempfile
        import zipfile

        output_file = options.output_file or self.create_temp_file(".zip")
        device = paddle.device.get_device()

        try:
            # 初始化PaddleOCR pipeline
            pipeline = PPStructureV3(device=device)
            logger.info(f"Start using PaddleOCR to process file: {input_file}")

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
                    for root, dirs, files in os.walk(temp_path):
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

            raise PDFProcessingError(error_msg)
