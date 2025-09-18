"""
通用资源管理器实现
"""

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, List, Optional
from uuid import uuid4

from ..interfaces.processor import IResourceManager
from ..utils.logging import get_logger

logger = get_logger("resource_manager")


class FileResourceManager(IResourceManager):
    """
    文件资源管理器实现
    负责临时文件、目录的创建和清理
    """

    def __init__(self, temp_dir: Optional[Path] = None):
        """
        初始化资源管理器

        Args:
            temp_dir: 临时目录路径，如果为None则使用系统默认
        """
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "pdftool"
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"资源管理器初始化，临时目录: {self.temp_dir}")

    def create_temp_file(self, suffix: str = "", prefix: str = "temp") -> Path:
        """创建临时文件"""
        try:
            # 确保后缀以点开头
            if suffix and not suffix.startswith("."):
                suffix = f".{suffix}"

            # 使用 tempfile 创建临时文件
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.temp_dir)
            # 关闭文件描述符，但保留文件
            import os

            os.close(fd)

            temp_file = Path(temp_path)
            logger.debug(f"创建临时文件: {temp_file}")
            return temp_file

        except Exception as e:
            logger.error(f"创建临时文件失败: {str(e)}")
            raise RuntimeError(f"Failed to create temp file: {str(e)}")

    def create_temp_dir(self, prefix: str = "temp") -> Path:
        """创建临时目录"""
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix, dir=self.temp_dir)
            temp_path = Path(temp_dir)
            logger.debug(f"创建临时目录: {temp_path}")
            return temp_path

        except Exception as e:
            logger.error(f"创建临时目录失败: {str(e)}")
            raise RuntimeError(f"Failed to create temp directory: {str(e)}")

    def cleanup_resources(self, resources: List[Any]) -> None:
        """清理资源"""
        cleaned = 0
        failed = 0

        for resource in resources:
            try:
                path = Path(resource) if not isinstance(resource, Path) else resource

                if path.is_file():
                    path.unlink()
                    cleaned += 1
                    logger.debug(f"删除文件: {path}")
                elif path.is_dir():
                    shutil.rmtree(path)
                    cleaned += 1
                    logger.debug(f"删除目录: {path}")
                else:
                    logger.warning(f"资源不存在，跳过: {path}")

            except Exception as e:
                failed += 1
                logger.warning(f"清理资源失败 {resource}: {str(e)}")

        if cleaned > 0:
            logger.info(f"资源清理完成: {cleaned} 个成功, {failed} 个失败")

    def create_archive(self, files: List[Any], output_path: Optional[Any] = None) -> Path:
        """创建归档文件"""
        try:
            # 确定输出路径
            if output_path is None:
                output_path = self.create_temp_file(suffix=".zip", prefix="archive_")
            else:
                output_path = Path(output_path)

            # 创建ZIP归档
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in files:
                    file_path = Path(file) if not isinstance(file, Path) else file
                    if file_path.is_file():
                        # 使用文件名作为归档中的名称
                        zf.write(file_path, file_path.name)
                        logger.debug(f"添加文件到归档: {file_path.name}")

            logger.info(f"创建归档文件: {output_path} (包含 {len(files)} 个文件)")
            return output_path

        except Exception as e:
            logger.error(f"创建归档文件失败: {str(e)}")
            raise RuntimeError(f"Failed to create archive: {str(e)}")

    def get_temp_dir(self) -> Path:
        """获取临时目录路径"""
        return self.temp_dir

    def get_temp_file_with_name(self, filename: str) -> Path:
        """根据文件名创建临时文件路径"""
        temp_file = self.temp_dir / f"{uuid4().hex}_{filename}"
        return temp_file

    def ensure_temp_dir_exists(self) -> None:
        """确保临时目录存在"""
        self.temp_dir.mkdir(exist_ok=True, parents=True)

    def cleanup_old_files(self, max_age_hours: int = 24) -> None:
        """清理超过指定时间的旧文件"""
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        cleaned = 0
        try:
            for file_path in self.temp_dir.rglob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned += 1
                        logger.debug(f"清理过期文件: {file_path}")

            if cleaned > 0:
                logger.info(f"清理了 {cleaned} 个过期文件")

        except Exception as e:
            logger.warning(f"清理过期文件时出错: {str(e)}")


class MemoryResourceManager(IResourceManager):
    """
    内存资源管理器实现
    主要用于测试或不需要文件持久化的场景
    """

    def __init__(self):
        self._temp_data = {}
        self._counter = 0

    def create_temp_file(self, suffix: str = "", prefix: str = "temp") -> str:
        """创建临时文件标识符"""
        self._counter += 1
        temp_id = f"{prefix}_{self._counter}{suffix}"
        self._temp_data[temp_id] = b""
        return temp_id

    def create_temp_dir(self, prefix: str = "temp") -> str:
        """创建临时目录标识符"""
        self._counter += 1
        temp_id = f"{prefix}_dir_{self._counter}"
        self._temp_data[temp_id] = {}
        return temp_id

    def cleanup_resources(self, resources: List[Any]) -> None:
        """清理内存资源"""
        for resource in resources:
            if resource in self._temp_data:
                del self._temp_data[resource]

    def create_archive(self, files: List[Any], output_path: Optional[Any] = None) -> str:
        """创建内存归档"""
        if output_path is None:
            output_path = self.create_temp_file(suffix=".zip", prefix="archive_")

        # 简单的内存归档实现
        archive_data = {"files": files, "type": "archive"}
        self._temp_data[output_path] = archive_data
        return output_path

    def get_data(self, resource_id: str) -> Any:
        """获取资源数据"""
        return self._temp_data.get(resource_id)

    def set_data(self, resource_id: str, data: Any) -> None:
        """设置资源数据"""
        self._temp_data[resource_id] = data
