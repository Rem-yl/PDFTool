"""
PDF密码保护操作
"""

import logging
from pathlib import Path
from uuid import uuid4

import PyPDF2

from ....common.exceptions import PDFProcessingError, PDFValidationError
from ....common.interfaces import BasePDFOperation
from ....common.models import OperationResult, PasswordProtectionOptions

logger = logging.getLogger(__name__)


class PasswordProtectionOperation(BasePDFOperation):
    """PDF密码保护操作实现"""

    @property
    def operation_name(self) -> str:
        return "password"

    def validate_input(self, input_file: Path, options: PasswordProtectionOptions) -> None:
        """验证密码保护操作输入"""
        self.validate_pdf_file(input_file)

        if not options.user_password:
            raise PDFValidationError("用户密码不能为空")

        if len(options.user_password) < 4:
            raise PDFValidationError("密码长度至少为4位")

    def execute(self, input_file: Path, options: PasswordProtectionOptions) -> OperationResult:
        """执行PDF密码保护操作"""
        self.validate_input(input_file, options)

        output_file = options.output_file or self.temp_dir / f"protected_{uuid4().hex}.pdf"

        try:
            with open(input_file, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                writer = PyPDF2.PdfWriter()

                # 复制所有页面
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    writer.add_page(page)

                # 复制元数据（如果存在）
                if reader.metadata:
                    writer.add_metadata(reader.metadata)

                # 设置密码和权限
                # 使用所有者密码（如果提供）或用户密码作为所有者密码
                owner_password = options.owner_password or options.user_password

                # 构建权限标志
                permissions = 0
                if options.allow_printing:
                    permissions |= 4  # 允许打印
                if options.allow_modification:
                    permissions |= 8  # 允许修改内容
                if options.allow_copying:
                    permissions |= 16  # 允许复制/提取文本
                if options.allow_annotation:
                    permissions |= 32  # 允许添加注释
                if options.allow_filling_forms:
                    permissions |= 256  # 允许填写表单
                if options.allow_screen_readers:
                    permissions |= 512  # 允许屏幕阅读器访问
                if options.allow_assembly:
                    permissions |= 1024  # 允许组装文档
                if options.allow_degraded_printing:
                    permissions |= 4  # 允许低质量打印

                # 加密PDF
                writer.encrypt(
                    user_password=options.user_password,
                    owner_password=owner_password,
                    permissions_flag=permissions,
                )

                # 写入输出文件
                with open(output_file, "wb") as output_f:
                    writer.write(output_f)

            logger.info(f"成功为PDF添加密码保护: {input_file}")

            # 构建权限描述
            permissions_desc = []
            if options.allow_printing:
                permissions_desc.append("打印")
            if options.allow_copying:
                permissions_desc.append("复制")
            if options.allow_modification:
                permissions_desc.append("修改")
            if options.allow_annotation:
                permissions_desc.append("注释")
            if options.allow_filling_forms:
                permissions_desc.append("填写表单")

            permissions_text = ", ".join(permissions_desc) if permissions_desc else "无权限"

            return OperationResult(
                success=True,
                message="PDF密码保护设置成功",
                output_files=[output_file],
                details=f"已设置用户密码，允许的操作: {permissions_text}",
            )

        except Exception as e:
            raise PDFProcessingError(f"密码保护失败: {str(e)}")
