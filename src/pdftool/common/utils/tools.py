from pathlib import Path
from typing import List


# REM: 清除web.dependencies中的工具代码, 移到这里来
def create_archive(file_paths: List[Path], output_zip="output.zip"):
    """
    将多个文件打包成一个 zip 压缩包

    Args:
        file_paths (List[Union[str, Path]]): 要打包的文件路径列表
        output_zip (str): 输出的 zip 文件路径
    """
    import os
    import zipfile

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            if isinstance(file, str):
                file = Path(file)
            if not file.exists():
                raise FileNotFoundError(f"File not found: {file}")

            arcname = os.path.basename(file)  # 只保留文件名，不带路径
            zipf.write(file, arcname)

    return output_zip
