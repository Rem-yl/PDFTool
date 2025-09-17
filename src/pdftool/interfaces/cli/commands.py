"""
CLI命令定义

定义所有的命令行接口命令。
"""

from pathlib import Path
from typing import List, Optional

import click

from ...common.exceptions import PDFToolError
from ...common.models import MergeOptions, SplitOptions, WatermarkOptions
from ...core.processor import PDFProcessor


@click.group()
@click.version_option()
def cli():
    """PDFTool - 强大的PDF操作工具"""
    pass


@cli.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--output", "-o", help="输出文件名", required=True)
@click.option("--temp-dir", help="临时目录", type=click.Path())
def merge(files: tuple, output: str, temp_dir: Optional[str]):
    """合并多个PDF文件"""
    try:
        processor = PDFProcessor(temp_dir=Path(temp_dir) if temp_dir else None)
        file_paths = [Path(f) for f in files]

        options = MergeOptions(output_filename=output)
        result = processor.merge_pdfs(file_paths, options)

        if result.success:
            click.echo(f"✅ 成功合并到: {result.output_file}")
        else:
            click.echo(f"❌ 合并失败: {result.error}")

    except PDFToolError as e:
        click.echo(f"❌ 错误: {e}")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["all", "page_range"]), default="all", help="拆分模式")
@click.option("--start", type=int, help="起始页码（page_range模式）")
@click.option("--end", type=int, help="结束页码（page_range模式）")
@click.option("--output-dir", "-o", help="输出目录", required=True)
@click.option("--temp-dir", help="临时目录", type=click.Path())
def split(
    file: str,
    mode: str,
    start: Optional[int],
    end: Optional[int],
    output_dir: str,
    temp_dir: Optional[str],
):
    """拆分PDF文件"""
    try:
        processor = PDFProcessor(temp_dir=Path(temp_dir) if temp_dir else None)
        file_path = Path(file)

        if mode == "page_range" and (start is None or end is None):
            click.echo("❌ page_range模式需要指定--start和--end")
            return

        options = SplitOptions(
            mode=mode, start_page=start, end_page=end, output_directory=output_dir
        )

        result = processor.split_pdf(file_path, options)

        if result.success:
            click.echo(f"✅ 成功拆分到: {result.output_file}")
        else:
            click.echo(f"❌ 拆分失败: {result.error}")

    except PDFToolError as e:
        click.echo(f"❌ 错误: {e}")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
def info(file: str):
    """获取PDF文件信息"""
    try:
        processor = PDFProcessor()
        file_path = Path(file)

        result = processor.get_pdf_info(file_path)

        if result.success:
            info_data = result.data
            click.echo(f"📄 文件: {file_path.name}")
            click.echo(f"📑 页数: {info_data.page_count}")
            click.echo(f"📏 大小: {info_data.file_size} bytes")
            click.echo(f"📅 创建时间: {info_data.creation_date or 'N/A'}")
            click.echo(f"✏️  作者: {info_data.author or 'N/A'}")
            click.echo(f"📝 标题: {info_data.title or 'N/A'}")
        else:
            click.echo(f"❌ 获取信息失败: {result.error}")

    except PDFToolError as e:
        click.echo(f"❌ 错误: {e}")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--text", help="水印文本")
@click.option("--image", help="水印图片路径", type=click.Path())
@click.option(
    "--position",
    type=click.Choice(["center", "top-left", "top-right", "bottom-left", "bottom-right"]),
    default="center",
    help="水印位置",
)
@click.option("--opacity", type=float, default=0.5, help="透明度 (0.0-1.0)")
@click.option("--output", "-o", help="输出文件名", required=True)
@click.option("--temp-dir", help="临时目录", type=click.Path())
def watermark(
    file: str,
    text: Optional[str],
    image: Optional[str],
    position: str,
    opacity: float,
    output: str,
    temp_dir: Optional[str],
):
    """添加水印到PDF文件"""
    try:
        if not text and not image:
            click.echo("❌ 必须指定--text或--image")
            return

        processor = PDFProcessor(temp_dir=Path(temp_dir) if temp_dir else None)
        file_path = Path(file)

        options = WatermarkOptions(
            text=text, image=image, position=position, opacity=opacity, output_filename=output
        )

        result = processor.add_watermark(file_path, options)

        if result.success:
            click.echo(f"✅ 成功添加水印到: {result.output_file}")
        else:
            click.echo(f"❌ 添加水印失败: {result.error}")

    except PDFToolError as e:
        click.echo(f"❌ 错误: {e}")


def create_cli_app():
    """创建CLI应用"""
    return cli
