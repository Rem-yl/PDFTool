# PDFTool 项目架构详细文档

## 📋 目录

- [项目概述](#项目概述)
- [架构设计](#架构设计)
- [目录结构](#目录结构)
- [核心组件](#核心组件)
- [数据模型](#数据模型)
- [API 接口](#api-接口)
- [GUI 应用](#gui-应用)
- [配置管理](#配置管理)
- [开发工具](#开发工具)
- [部署指南](#部署指南)
- [扩展开发](#扩展开发)

---

## 🎯 项目概述

**PDFTool** 是一个综合性的PDF文档处理工具，提供三种使用接口：

### 核心功能
- **PDF合并**: 将多个PDF文件合并为一个
- **PDF拆分**: 按页面或范围拆分PDF文件
- **PDF信息提取**: 获取PDF元数据和属性信息

### 三种接口
1. **桌面GUI应用** (`pdftool-gui`): 基于Tkinter的现代化桌面界面
2. **Web API** (`pdftool-api`): FastAPI驱动的REST API服务
3. **命令行CLI**: 直接调用核心功能的命令行接口

---

## 🏗️ 架构设计

### 设计原则

PDFTool采用**分层架构模式**，遵循以下设计原则：

```
┌─────────────────────────────────────────┐
│           用户接口层 (UI Layer)            │
├─────────────────┬───────────┬───────────┤
│   GUI (Tkinter) │ Web API   │    CLI    │
│                 │(FastAPI)  │           │
└─────────────────┴───────────┴───────────┘
┌─────────────────────────────────────────┐
│         业务逻辑层 (Business Layer)        │
├─────────────────────────────────────────┤
│     PDFOperations (核心处理引擎)          │
│   • merge_pdfs() • split_pdf()          │
│   • get_pdf_info() • validate_pdf()     │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│          数据层 (Data Layer)             │
├─────────────────────────────────────────┤
│   Models • Settings • Exceptions        │
│   Logging • Validators • Utils         │
└─────────────────────────────────────────┘
```

### 核心设计模式

1. **单一职责原则**: 每个模块负责特定功能
2. **依赖注入**: 通过配置系统管理依赖
3. **异常层次化**: 自定义异常继承体系
4. **工厂模式**: PDFOperations作为核心工厂类
5. **策略模式**: 不同分割模式的实现

---

## 📁 目录结构

```
pdftool/
├── 📁 src/pdftool/              # 主要源码目录
│   ├── 📁 core/                 # 核心业务逻辑
│   │   ├── pdf_operations.py    # 📋 PDF操作核心引擎
│   │   ├── models.py            # 📊 数据模型定义
│   │   └── exceptions.py        # ⚠️ 自定义异常类
│   ├── 📁 api/                  # Web API 接口
│   │   ├── main.py              # 🌐 FastAPI应用主文件
│   │   └── templates.py         # 🎨 HTML模板管理
│   ├── 📁 gui/                  # 桌面GUI应用
│   │   └── main.py              # 🖥️ Tkinter GUI主程序
│   ├── 📁 config/               # 配置管理
│   │   └── settings.py          # ⚙️ 应用配置类
│   └── 📁 utils/                # 工具模块
│       ├── logging.py           # 📝 日志配置
│       └── validators.py        # ✅ 输入验证工具
├── 📁 tests/                    # 测试代码
│   └── test_pdf_operations.py   # 🧪 核心功能测试
├── 📄 pyproject.toml            # 📦 项目配置和依赖
├── 📄 Makefile                  # 🔧 开发命令集合
├── 📄 CLAUDE.md                 # 🤖 Claude Code 指南
├── 📄 README.md                 # 📖 项目说明文档
└── 📄 requirements.txt          # 📋 Python依赖列表
```

---

## 🔧 核心组件

### 1. PDFOperations 引擎 (`core/pdf_operations.py`)

**核心处理引擎**，所有PDF操作的入口点：

```python
class PDFOperations:
    """PDF操作核心引擎"""
    
    def __init__(self, temp_dir: Optional[Path] = None):
        """初始化操作引擎"""
        self.temp_dir = temp_dir or Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    # 核心方法
    def merge_pdfs(self, files: List[Path], options: MergeOptions) -> OperationResult
    def split_pdf(self, file_path: Path, options: SplitOptions) -> OperationResult  
    def get_pdf_info(self, file_path: Path) -> PDFInfo
    def validate_pdf_file(self, file_path: Path) -> None
```

**设计特点**:
- 统一的结果返回格式 (`OperationResult`)
- 完整的错误处理和验证
- 临时文件自动管理
- 支持批量操作

### 2. 异常处理系统 (`core/exceptions.py`)

**层次化异常设计**:

```python
PDFToolError (基础异常)
├── PDFValidationError    # 文件验证错误
├── PDFProcessingError    # 处理过程错误
└── PDFFileNotFoundError  # 文件未找到错误
```

### 3. 配置系统 (`config/settings.py`)

**环境变量驱动的配置系统**:

```python
class Settings(BaseSettings):
    # 应用配置
    app_name: str = "PDFTool"
    version: str = "1.0.0"
    debug: bool = False
    
    # 文件处理
    temp_dir: Path = Path("temp")
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # API设置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # 日志配置
    log_level: str = "INFO"
```

**环境变量前缀**: 所有配置都支持 `PDFTOOL_` 前缀的环境变量覆盖

---

## 📊 数据模型

### 核心数据结构 (`core/models.py`)

```python
@dataclass
class PDFInfo:
    """PDF元数据信息"""
    pages: int                           # 页数
    title: Optional[str]                # 标题
    author: Optional[str]               # 作者
    creation_date: Optional[datetime]   # 创建日期
    file_size: Optional[int]            # 文件大小
    file_path: Optional[Path]           # 文件路径

@dataclass  
class SplitOptions:
    """PDF拆分选项"""
    mode: SplitMode                     # 拆分模式
    start_page: Optional[int]           # 起始页
    end_page: Optional[int]             # 结束页
    output_dir: Optional[Path]          # 输出目录
    filename_prefix: Optional[str]      # 文件名前缀

@dataclass
class MergeOptions:
    """PDF合并选项"""
    output_file: Optional[Path]         # 输出文件
    preserve_bookmarks: bool = True     # 保留书签
    preserve_metadata: bool = True      # 保留元数据

@dataclass
class OperationResult:
    """操作结果标准化返回"""
    success: bool                       # 是否成功
    message: str                        # 结果消息
    output_files: List[Path]            # 输出文件列表
    details: Optional[str]              # 详细信息
```

### 枚举类型

```python
class SplitMode(Enum):
    """PDF拆分模式"""
    ALL_PAGES = "all"     # 每页单独拆分
    PAGE_RANGE = "range"  # 指定页面范围
```

---

## 🌐 API 接口

### Web界面架构

新的**功能选择式架构**提供直观的用户体验：

```
首页 (/) 
├── 功能选择卡片界面
│   ├── 📄 PDF合并 → /merge
│   ├── ✂️ PDF拆分 → /split  
│   └── ℹ️ PDF信息 → /info
└── 各功能独立页面
    ├── 专用UI界面
    ├── 文件上传区域
    ├── 参数配置选项
    └── 结果显示区域
```

### API 端点

#### 页面路由
- `GET /` - 功能选择主页面
- `GET /merge` - PDF合并页面  
- `GET /split` - PDF拆分页面
- `GET /info` - PDF信息页面
- `GET /health` - 健康检查

#### 功能API
- `POST /merge` - PDF合并处理
- `POST /split` - PDF拆分处理  
- `POST /info` - PDF信息提取

### API 请求示例

#### PDF合并
```bash
curl -X POST "http://localhost:8000/merge" \
  -F "files=@file1.pdf" \
  -F "files=@file2.pdf"
```

#### PDF拆分
```bash  
curl -X POST "http://localhost:8000/split" \
  -F "file=@document.pdf" \
  -F "mode=range" \
  -F "start_page=1" \
  -F "end_page=5"
```

#### PDF信息
```bash
curl -X POST "http://localhost:8000/info" \
  -F "file=@document.pdf"
```

### 响应格式

**文件下载响应**: 直接返回文件流
**信息查询响应**: JSON格式
```json
{
  "pages": 10,
  "title": "示例文档", 
  "author": "作者姓名",
  "creation_date": "2024-01-01T00:00:00",
  "file_size": 1048576
}
```

---

## 🖥️ GUI 应用

### Tkinter现代化界面

GUI应用 (`gui/main.py`) 提供友好的桌面体验：

#### 主要特性
- **标签页界面**: 功能分离，操作直观
- **拖拽支持**: 文件拖拽到应用窗口
- **进度指示**: 实时操作进度显示
- **结果预览**: 操作完成后的结果展示

#### 界面组件
```python
class ModernPDFTool:
    """现代化PDF工具GUI"""
    
    def __init__(self, root: tk.Tk):
        self.setup_main_window()    # 主窗口配置
        self.setup_styles()         # 样式设置
        self.create_widgets()       # 创建界面组件
    
    # 功能标签页
    def create_merge_tab()          # PDF合并标签
    def create_split_tab()          # PDF拆分标签  
    def create_info_tab()           # PDF信息标签
```

#### 启动方式
```bash
# 命令行启动
pdftool-gui

# 或者直接运行
python -m pdftool.gui.main

# 使用Makefile
make run-gui
```

---

## ⚙️ 配置管理

### 环境变量配置

所有配置项都支持环境变量覆盖，前缀为 `PDFTOOL_`：

```bash
# 应用配置
export PDFTOOL_DEBUG=true
export PDFTOOL_APP_NAME="自定义PDF工具"

# 文件处理
export PDFTOOL_TEMP_DIR="/tmp/pdftool"
export PDFTOOL_MAX_FILE_SIZE=52428800  # 50MB

# API服务
export PDFTOOL_API_HOST="127.0.0.1"
export PDFTOOL_API_PORT=9000
export PDFTOOL_API_WORKERS=4

# 日志配置
export PDFTOOL_LOG_LEVEL="DEBUG"
export PDFTOOL_LOG_FILE="/var/log/pdftool.log"
```

### .env 文件配置

创建 `.env` 文件进行本地配置：

```env
# .env 文件示例
PDFTOOL_DEBUG=true
PDFTOOL_TEMP_DIR=./temp
PDFTOOL_API_PORT=8000
PDFTOOL_LOG_LEVEL=INFO
```

### 配置优先级

1. 环境变量 (最高优先级)
2. .env 文件
3. 代码中的默认值 (最低优先级)

---

## 🔧 开发工具

### Makefile 命令

项目提供完整的Makefile支持常见开发任务：

#### 安装和设置
```bash
make install          # 安装基础包
make install-dev       # 安装开发依赖
```

#### 代码质量
```bash
make lint             # 代码检查 (flake8, mypy, black)
make format           # 代码格式化 (black, isort)
```

#### 测试
```bash
make test             # 运行测试
make test-cov         # 测试 + 覆盖率报告
```

#### 运行应用
```bash
make run-gui          # 启动GUI应用
make run-api          # 启动API服务
make dev-api          # 开发模式API (热重载)
```

#### 构建和清理
```bash
make build            # 构建分发包
make clean            # 清理构建文件
```

#### Docker支持
```bash
make docker-build     # 构建Docker镜像
make docker-run       # 运行Docker容器
```

### 依赖管理

#### 核心依赖
```toml
dependencies = [
    "PyPDF2>=3.0.0",           # PDF处理引擎
    "fastapi>=0.104.0",        # Web框架
    "uvicorn>=0.24.0",         # ASGI服务器
    "python-multipart>=0.0.6", # 文件上传支持
]
```

#### 开发依赖
```toml
dev = [
    "pytest>=7.0.0",          # 测试框架
    "pytest-cov>=4.0.0",      # 测试覆盖率
    "black>=22.0.0",          # 代码格式化
    "flake8>=5.0.0",          # 代码检查
    "mypy>=1.0.0",            # 类型检查
    "pre-commit>=2.20.0",     # Git钩子
]
```

### 代码质量标准

#### Black配置
- 行长度: 100字符
- 目标版本: Python 3.8+

#### MyPy配置
- 严格类型检查
- 不允许未类型化的函数定义
- 警告未使用的导入

#### 测试配置
- 测试目录: `tests/`
- 覆盖率要求: `src/pdftool`
- HTML报告生成: `htmlcov/`

---

## 🚀 部署指南

### 开发环境部署

#### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/Rem-yl/PDFTool.git
cd PDFTool

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
make install-dev
```

#### 2. 配置设置
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置
vim .env
```

#### 3. 运行测试
```bash
make test
make lint
```

### 生产环境部署

#### 1. 使用Docker (推荐)
```bash
# 构建镜像
make docker-build

# 运行容器
make docker-run

# 或使用docker-compose
docker-compose up --build
```

#### 2. 直接部署
```bash
# 安装生产依赖
pip install -e ".[api]"

# 启动API服务
uvicorn pdftool.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用gunicorn
gunicorn pdftool.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 3. 系统服务配置

**systemd服务配置** (`/etc/systemd/system/pdftool.service`):
```ini
[Unit]
Description=PDFTool API Service
After=network.target

[Service]
Type=simple
User=pdftool
WorkingDirectory=/opt/pdftool
Environment=PDFTOOL_LOG_LEVEL=INFO
Environment=PDFTOOL_API_WORKERS=4
ExecStart=/opt/pdftool/venv/bin/uvicorn pdftool.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 反向代理配置

**Nginx配置示例**:
```nginx
server {
    listen 80;
    server_name pdftool.example.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔌 扩展开发

### 添加新的PDF操作

#### 1. 扩展核心引擎

在 `core/pdf_operations.py` 中添加新方法：

```python
def compress_pdf(self, file_path: Path, options: CompressionOptions) -> OperationResult:
    """PDF压缩功能"""
    try:
        self.validate_pdf_file(file_path)
        
        # 实现压缩逻辑
        output_file = self.temp_dir / f"compressed_{uuid4().hex}.pdf"
        
        # ... 压缩处理代码 ...
        
        return OperationResult(
            success=True,
            message="PDF压缩成功",
            output_files=[output_file]
        )
    except PDFToolError as e:
        return OperationResult(
            success=False,
            message=str(e),
            output_files=[]
        )
```

#### 2. 添加数据模型

在 `core/models.py` 中定义选项类：

```python
@dataclass
class CompressionOptions:
    """PDF压缩选项"""
    quality: float = 0.7          # 压缩质量 (0.1-1.0)
    compress_images: bool = True   # 压缩图片
    remove_metadata: bool = False  # 移除元数据
```

#### 3. 扩展API接口

在 `api/main.py` 中添加新端点：

```python
@app.post("/compress")
async def compress_pdf(file: UploadFile = File(...), quality: float = Form(0.7)):
    """PDF压缩接口"""
    # 实现接口逻辑
    pass
```

#### 4. 扩展GUI界面

在 `gui/main.py` 中添加新标签页：

```python
def create_compress_tab(self):
    """创建压缩功能标签页"""
    # 实现GUI组件
    pass
```

### 自定义配置选项

在 `config/settings.py` 中添加新配置：

```python
class Settings(BaseSettings):
    # 新增配置项
    compression_quality: float = Field(default=0.7, env="PDFTOOL_COMPRESSION_QUALITY")
    enable_ocr: bool = Field(default=False, env="PDFTOOL_ENABLE_OCR")
```

### 插件系统架构

为支持插件扩展，可以考虑以下架构：

```python
# plugin_manager.py
class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name: str, plugin_class):
        """注册插件"""
        self.plugins[name] = plugin_class
    
    def get_plugin(self, name: str):
        """获取插件实例"""
        return self.plugins.get(name)

# 插件基类
class PDFPlugin:
    """PDF插件基类"""
    
    def process(self, file_path: Path, options: dict) -> OperationResult:
        """插件处理方法"""
        raise NotImplementedError
```

### 测试新功能

为新功能编写测试：

```python
# tests/test_compression.py
def test_compress_pdf():
    """测试PDF压缩功能"""
    pdf_ops = PDFOperations()
    options = CompressionOptions(quality=0.7)
    
    result = pdf_ops.compress_pdf(test_file, options)
    
    assert result.success
    assert len(result.output_files) == 1
```

---

## 📚 附录

### 常见问题解答

#### Q: 如何修改最大文件大小限制？
A: 设置环境变量 `PDFTOOL_MAX_FILE_SIZE=209715200` (200MB)

#### Q: 如何启用调试模式？
A: 设置 `PDFTOOL_DEBUG=true`

#### Q: 如何自定义临时文件目录？
A: 设置 `PDFTOOL_TEMP_DIR=/path/to/temp`

#### Q: 如何添加新的PDF处理功能？
A: 参考[扩展开发](#扩展开发)章节

### 相关链接

- **项目仓库**: https://github.com/Rem-yl/PDFTool
- **问题反馈**: https://github.com/Rem-yl/PDFTool/issues
- **PyPDF2文档**: https://pypdf2.readthedocs.io/
- **FastAPI文档**: https://fastapi.tiangolo.com/

### 版本历史

- **v1.0.0**: 初始版本，基础PDF操作功能
- **v1.1.0**: 添加Web界面功能选择架构
- **v1.2.0**: 计划添加PDF压缩和OCR功能

---

*此文档由 PDFTool 开发团队维护，最后更新：2024年*