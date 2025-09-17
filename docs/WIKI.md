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
- **PDF水印**: 添加文本或图片水印，支持9个位置和透明度调节

### 三种接口
1. **桌面GUI应用** (`pdftool-gui`): 基于Tkinter的现代化桌面界面
2. **Web API** (`pdftool-api`): FastAPI驱动的REST API服务
3. **命令行CLI**: 直接调用核心功能的命令行接口

---

## 🏗️ 架构设计

### 设计原则

PDFTool采用**插件式架构模式** (PDF-3重构)，具有高度可扩展性：

```
┌─────────────────────────────────────────┐
│           用户接口层 (UI Layer)            │
├─────────────────┬───────────┬───────────┤
│   GUI (Tkinter) │ Web API   │    CLI    │
│                 │(FastAPI)  │           │
└─────────────────┴───────────┴───────────┘
┌─────────────────────────────────────────┐
│         路由层 (Router Layer)           │
├─────────────────────────────────────────┤
│   Web Routes │ PDF API │ Health │ Docs │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│        中间件层 (Middleware Layer)        │
├─────────────────────────────────────────┤
│  CORS │ Error Handler │ Logging │ Auth  │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│      服务处理层 (Service Handler)        │
├─────────────────────────────────────────┤
│Watermark│Merge│Split│Info│ServiceRegistry│
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│      策略引擎层 (Strategy Engine)        │
├─────────────────────────────────────────┤
│    PDFProcessor + OperationFactory      │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│        操作插件层 (Operations)           │
├─────────────────────────────────────────┤
│ WatermarkOp │ MergeOp │ SplitOp │ InfoOp │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│          核心层 (Core Layer)             │
├─────────────────────────────────────────┤
│         PDF引擎 (PyPDF2/Reportlab)       │
└─────────────────────────────────────────┘
```

### 核心设计模式

1. **策略模式**: PDF操作通过可插拔的策略实现
2. **工厂模式**: OperationFactory管理操作类的创建和注册
3. **服务注册模式**: API服务可动态注册和发现
4. **依赖注入**: 通过ServiceManager统一管理依赖
5. **接口隔离**: 清晰的接口定义实现解耦
6. **单一职责**: 每个操作类专注于单一功能
7. **开闭原则**: 对扩展开放，对修改封闭

### 架构优势

- **高扩展性**: 新功能通过插件方式添加，无需修改核心代码
- **解耦设计**: 各层职责单一，便于测试和维护
- **策略引擎**: 支持动态选择和注册PDF操作
- **服务注册**: API服务可以运行时注册和发现
- **向后兼容**: 现有功能保持不变，平滑升级

---

## 📁 目录结构

```
pdftool/
├── 📁 src/pdftool/              # 主要源码目录
│   ├── 📁 core/                 # 核心业务逻辑
│   │   ├── interfaces.py        # 🔌 核心接口定义
│   │   ├── operation_factory.py # 🏭 操作工厂
│   │   ├── pdf_processor.py     # ⚙️ PDF处理器(新架构)
│   │   ├── pdf_operations.py    # 📋 PDF操作引擎(兼容)
│   │   ├── models.py            # 📊 数据模型定义
│   │   ├── exceptions.py        # ⚠️ 自定义异常类
│   │   └── 📁 operations/       # 🔌 操作插件
│   │       ├── watermark.py     # 💧 水印操作
│   │       ├── merge.py         # 📄 合并操作
│   │       ├── split.py         # ✂️ 拆分操作
│   │       └── info.py          # ℹ️ 信息提取操作
│   ├── 📁 api/                  # Web API 接口
│   │   ├── main.py              # 🌐 FastAPI应用主文件
│   │   ├── app.py               # 🏗️ 应用工厂
│   │   ├── interfaces.py        # 🔌 API接口定义
│   │   ├── service_manager.py   # 👔 服务管理器
│   │   ├── service_registry.py  # 📋 服务注册表
│   │   ├── dependencies.py      # 🔗 依赖注入
│   │   ├── 📁 handlers/         # 🎯 服务处理器
│   │   │   ├── watermark.py     # 💧 水印服务处理器
│   │   │   ├── merge.py         # 📄 合并服务处理器
│   │   │   ├── split.py         # ✂️ 拆分服务处理器
│   │   │   └── info.py          # ℹ️ 信息服务处理器
│   │   ├── 📁 routers/          # 🛣️ 路由模块
│   │   │   ├── web.py           # 🌐 Web界面路由
│   │   │   ├── pdf.py           # 📄 PDF处理API路由
│   │   │   ├── health.py        # ❤️ 健康检查路由
│   │   │   └── docs.py          # 📚 API文档路由
│   │   ├── 📁 middleware/       # 🔧 中间件层
│   │   ├── 📁 schemas/          # 📊 数据模式定义
│   │   └── 📁 templates/        # 🎨 前端模板
│   ├── 📁 gui/                  # 桌面GUI应用
│   │   └── main.py              # 🖥️ Tkinter GUI主程序
│   ├── 📁 config/               # 配置管理
│   │   └── settings.py          # ⚙️ 应用配置类
│   └── 📁 utils/                # 工具模块
│       ├── logging.py           # 📝 日志配置
│       └── validators.py        # ✅ 输入验证工具
├── 📁 tests/                    # 测试代码
│   └── test_pdf_operations.py   # 🧪 核心功能测试
├── 📁 docs/                     # 项目文档
│   ├── PDF-3_REFACTOR.md        # 📋 重构文档
│   ├── WIKI.md                  # 📖 架构详细文档
│   └── TODO.md                  # 📝 开发计划
├── 📄 pyproject.toml            # 📦 项目配置和依赖
├── 📄 Makefile                  # 🔧 开发命令集合
├── 📄 CLAUDE.md                 # 🤖 Claude Code 指南
├── 📄 README.md                 # 📖 项目说明文档
└── 📄 requirements.txt          # 📋 Python依赖列表
```

---

## 🔧 核心组件

### 1. 核心接口层 (`core/interfaces.py`)

**统一接口定义**，为插件式架构提供标准化接口：

```python
class IPDFOperation(ABC):
    """PDF操作接口"""

    @abstractmethod
    def execute(self, input_file: Path, options: Any) -> OperationResult:
        """执行PDF操作"""
        pass

    @property
    @abstractmethod
    def operation_name(self) -> str:
        """操作名称"""
        pass

class IServiceHandler(ABC):
    """服务处理器接口"""

    @abstractmethod
    async def handle(self, files: List[UploadFile], request: Any) -> OperationResult:
        """处理API请求"""
        pass

    @property
    @abstractmethod
    def service_name(self) -> str:
        """服务名称"""
        pass
```

### 2. PDF处理器 (`core/pdf_processor.py`)

**新架构核心处理器**，基于策略模式的PDF操作引擎：

```python
class PDFProcessor:
    """基于策略模式的PDF处理器"""

    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path("temp")
        self.operation_factory = OperationFactory()

    def process(self, operation_name: str, input_file: Path, options: Any) -> OperationResult:
        """执行指定操作"""
        operation = self.operation_factory.create_operation(operation_name)
        return operation.execute(input_file, options)

    def register_operation(self, name: str, operation_class: Type[IPDFOperation]) -> None:
        """注册新操作"""
        self.operation_factory.register(name, operation_class)
```

### 3. 操作工厂 (`core/operation_factory.py`)

**工厂模式实现**，管理PDF操作类的创建和注册：

```python
class OperationFactory:
    """PDF操作工厂类"""

    def __init__(self):
        self._operations: Dict[str, Type[IPDFOperation]] = {}
        self._register_builtin_operations()

    def register(self, name: str, operation_class: Type[IPDFOperation]) -> None:
        """注册操作类"""
        self._operations[name] = operation_class

    def create_operation(self, name: str) -> IPDFOperation:
        """创建操作实例"""
        if name not in self._operations:
            raise ValueError(f"Unknown operation: {name}")
        return self._operations[name]()

    def list_operations(self) -> List[str]:
        """列出所有可用操作"""
        return list(self._operations.keys())
```

### 4. 操作插件层 (`core/operations/`)

**独立操作类**，每个PDF功能一个专用类：

```python
# core/operations/watermark.py
class WatermarkOperation(IPDFOperation):
    """水印操作插件"""

    @property
    def operation_name(self) -> str:
        return "watermark"

    def execute(self, input_file: Path, options: WatermarkOptions) -> OperationResult:
        """执行水印添加"""
        # 具体水印处理逻辑
        pass

# core/operations/merge.py
class MergeOperation(IPDFOperation):
    """合并操作插件"""

    @property
    def operation_name(self) -> str:
        return "merge"

    def execute(self, input_files: List[Path], options: MergeOptions) -> OperationResult:
        """执行PDF合并"""
        # 具体合并处理逻辑
        pass
```

### 5. 兼容性层 (`core/pdf_operations.py`)

**向后兼容的核心引擎**，保持原有API不变：

```python
class PDFOperations:
    """PDF操作核心引擎 - 兼容性包装器"""

    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        self.processor = PDFProcessor(temp_dir)

    # 保持原有方法签名
    def merge_pdfs(self, files: List[Path], options: MergeOptions) -> OperationResult:
        """合并PDF文件"""
        return self.processor.process("merge", files, options)

    def split_pdf(self, file_path: Path, options: SplitOptions) -> OperationResult:
        """拆分PDF文件"""
        return self.processor.process("split", file_path, options)

    def add_watermark(self, file_path: Path, options: WatermarkOptions) -> OperationResult:
        """添加水印"""
        return self.processor.process("watermark", file_path, options)

    def get_pdf_info(self, file_path: Path) -> PDFInfo:
        """获取PDF信息"""
        return self.processor.process("info", file_path, None)
```

**新架构特点**:
- 插件式扩展：新功能通过实现接口添加
- 动态注册：运行时注册新操作类
- 策略模式：灵活选择操作实现
- 向后兼容：原有代码无需修改
- 职责分离：每个组件专注单一功能

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

## 🌐 API 接口架构

### 插件式API架构

基于**服务注册模式**的现代化API架构设计：

```
src/pdftool/api/
├── 📁 app.py                    # 🏗️ FastAPI应用工厂
├── 📁 main.py                   # 🚀 应用入口点和启动器
├── 📁 interfaces.py             # 🔌 API服务接口定义
├── 📁 service_manager.py        # 👔 服务管理器
├── 📁 service_registry.py       # 📋 服务注册表
├── 📁 handlers/                 # 🎯 服务处理器 (NEW)
│   ├── watermark.py             # 💧 水印服务处理器
│   ├── merge.py                 # 📄 合并服务处理器
│   ├── split.py                 # ✂️ 拆分服务处理器
│   └── info.py                  # ℹ️ 信息服务处理器
├── 📁 routers/                  # 🛣️ 路由模块 (UPDATED)
│   ├── web.py                   # 🌐 Web界面路由
│   ├── pdf.py                   # 📄 统一PDF API路由 (v1)
│   ├── health.py                # ❤️ 健康检查路由
│   └── docs.py                  # 📚 API文档路由
├── 📁 middleware/               # 🔧 中间件层
│   ├── cors.py                  # 🌍 跨域处理
│   ├── error_handler.py         # ⚠️ 全局错误处理
│   └── logging.py               # 📝 请求日志记录
├── 📁 schemas/                  # 📊 数据模式定义
│   ├── requests.py              # 📥 请求模型
│   ├── responses.py             # 📤 响应模型
│   └── models.py                # 📋 数据传输对象
├── 📁 dependencies.py           # 🔗 依赖注入
├── 📁 templates/                # 🎨 前端模板 (UPDATED)
│   ├── base.html                # 🏗️ 基础模板
│   ├── index.html               # 🏠 功能选择首页
│   ├── merge.html               # 📄 PDF合并页面
│   ├── split.html               # ✂️ PDF拆分页面
│   ├── watermark.html           # 💧 PDF水印页面 (NEW)
│   ├── info.html                # ℹ️ PDF信息页面
│   └── static/                  # 📁 静态资源
│       ├── css/                 # 🎨 样式文件
│       └── js/                  # ⚡ JavaScript
└── 📁 utils/                    # 🛠️ API工具函数
```

### 新架构核心组件

#### 1. 服务管理器 (`api/service_manager.py`)

**统一服务管理**，负责服务的注册、发现和调用：

```python
class ServiceManager:
    """API服务管理器"""

    def __init__(self):
        self.registry = ServiceRegistry()
        self._register_builtin_services()

    def register_service(self, name: str, handler_class: Type[IServiceHandler]) -> None:
        """注册服务处理器"""
        self.registry.register(name, handler_class)

    async def handle_request(self, service_name: str, files: List[UploadFile],
                           request: Any) -> OperationResult:
        """处理API请求"""
        handler = self.registry.get_handler(service_name)
        return await handler.handle(files, request)

    def list_services(self) -> List[str]:
        """列出所有可用服务"""
        return self.registry.list_services()
```

#### 2. 服务处理器 (`api/handlers/`)

**专用处理器**，每个PDF功能对应一个API服务处理器：

```python
# api/handlers/watermark.py
class WatermarkServiceHandler(IServiceHandler):
    """水印服务处理器"""

    @property
    def service_name(self) -> str:
        return "watermark"

    async def handle(self, files: List[UploadFile],
                    request: WatermarkRequest) -> OperationResult:
        """处理水印添加请求"""
        # 验证请求参数
        # 调用核心水印操作
        # 返回结果
        pass

# api/handlers/merge.py
class MergeServiceHandler(IServiceHandler):
    """合并服务处理器"""

    @property
    def service_name(self) -> str:
        return "merge"

    async def handle(self, files: List[UploadFile],
                    request: MergeRequest) -> OperationResult:
        """处理PDF合并请求"""
        # 合并处理逻辑
        pass
```

#### 3. 统一PDF路由 (`api/routers/pdf.py`)

**版本化API端点**，所有PDF操作通过统一路由：

```python
@router.post("/api/v1/pdf/{operation}")
async def handle_pdf_operation(
    operation: str,
    files: List[UploadFile] = File(...),
    request_data: Dict[str, Any] = Depends(parse_form_data),
    service_manager: ServiceManager = Depends(get_service_manager)
):
    """统一PDF操作处理端点"""
    try:
        result = await service_manager.handle_request(operation, files, request_data)

        if result.success:
            return FileResponse(result.output_files[0])
        else:
            raise HTTPException(status_code=400, detail=result.message)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Unknown operation: {operation}")
```

### Web界面架构

**功能选择式用户体验**：

```
首页 (/) 
├── 🎯 功能选择卡片界面
│   ├── 📄 PDF合并 → /merge
│   ├── ✂️ PDF拆分 → /split  
│   └── ℹ️ PDF信息 → /info
└── 🎨 各功能独立页面
    ├── 专用UI界面设计
    ├── 拖拽文件上传区域
    ├── 智能参数配置选项
    └── 实时结果显示区域
```

### API 端点系统

#### Web界面路由 (router/web.py)
- `GET /` - 功能选择主页面
- `GET /merge` - PDF合并页面
- `GET /split` - PDF拆分页面
- `GET /watermark` - PDF水印页面 ✅ NEW
- `GET /info` - PDF信息页面

#### API v1 端点 (router/pdf.py)
- `POST /api/v1/pdf/merge` - PDF合并处理
- `POST /api/v1/pdf/split` - PDF拆分处理
- `POST /api/v1/pdf/watermark` - PDF水印处理 ✅ NEW
- `POST /api/v1/pdf/info` - PDF信息提取
- `GET /api/v1/pdf/services` - 服务发现端点 ✅ NEW
- `GET /api/v1/pdf/formats` - 支持格式查询

#### 系统监控端点 (router/health.py)
- `GET /health` - 健康检查
- `GET /health/ping` - 连通性检查

#### API文档端点 (router/docs.py)
- `GET /api/version` - API版本信息
- `GET /api/endpoints` - 端点列表
- `GET /api/status` - 系统状态
- `GET /api/docs` - Swagger文档
- `GET /api/redoc` - ReDoc文档

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

#### PDF水印 ✅ NEW
```bash
# 文本水印
curl -X POST "http://localhost:8000/api/v1/pdf/watermark" \
  -F "file=@document.pdf" \
  -F "watermark_type=text" \
  -F "watermark_text=CONFIDENTIAL" \
  -F "position=center" \
  -F "opacity=0.3" \
  -F "font_size=48" \
  -F "font_color=#FF0000" \
  -F "page_selection=all"

# 图片水印
curl -X POST "http://localhost:8000/api/v1/pdf/watermark" \
  -F "file=@document.pdf" \
  -F "watermark_type=image" \
  -F "watermark_image=@logo.png" \
  -F "position=bottom_right" \
  -F "opacity=0.5" \
  -F "image_scale=80" \
  -F "page_selection=pages" \
  -F "specific_pages=1,3,5"
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
- **水印功能**: 集成文本和图片水印操作 ✅ NEW

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
    def create_watermark_tab()      # PDF水印标签 ✅ NEW
    def create_info_tab()           # PDF信息标签

    # 水印功能方法 ✅ NEW
    def add_watermark_to_pdf()      # 添加水印到PDF
    def update_watermark_preview()  # 更新水印预览
    def browse_watermark_image()    # 浏览水印图片
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

## 🔌 扩展开发指南

### 完整功能扩展流程

本节详细说明如何向PDFTool添加新功能。以**PDF压缩功能**为例，展示完整的开发流程。

---

### 📋 开发步骤概览

```
1. 🎯 需求分析和设计
   ├── 功能需求定义
   ├── 接口设计
   └── 数据模型设计

2. 🔧 核心层实现 (Core Layer)
   ├── 扩展 PDFOperations 类
   ├── 添加数据模型
   └── 定义自定义异常

3. 🌐 API层实现 (API Layer)  
   ├── 创建服务层
   ├── 添加路由端点
   ├── 设计请求/响应模型
   └── 创建Web界面

4. 🖥️ GUI层实现 (GUI Layer)
   ├── 添加新标签页
   ├── 设计用户界面
   └── 实现事件处理

5. ⚙️ 配置和测试
   ├── 添加配置选项
   ├── 编写单元测试
   ├── 更新文档
   └── 验证功能
```

---

### 🎯 第一步：需求分析和设计

#### 功能需求定义

假设我们要添加**PDF压缩功能**：

```markdown
# PDF压缩功能需求

## 功能描述
- 减少PDF文件大小，提高传输和存储效率
- 支持多种压缩级别
- 保持可读性的同时最大化压缩比

## 用户接口
- Web界面: 上传PDF -> 选择压缩级别 -> 下载压缩后的文件
- GUI界面: 拖拽PDF文件 -> 配置压缩选项 -> 保存结果
- API接口: POST请求 -> 返回压缩文件

## 技术要求  
- 支持图片压缩
- 可选择移除元数据
- 压缩质量可调节 (0.1-1.0)
- 保持文档结构完整性
```

#### 接口设计

```python
# API接口设计
POST /api/v1/pdf/compress
Content-Type: multipart/form-data

参数:
- file: PDF文件
- quality: 压缩质量 (0.1-1.0)
- compress_images: 是否压缩图片
- remove_metadata: 是否移除元数据

响应:
- 成功: 返回压缩后的PDF文件
- 失败: 返回错误信息
```

---

### 🔧 第二步：核心层实现

#### 1. 扩展数据模型 (`core/models.py`)

```python
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class CompressionOptions:
    """PDF压缩选项配置"""
    quality: float = 0.7                    # 压缩质量 (0.1-1.0)
    compress_images: bool = True             # 压缩图片
    remove_metadata: bool = False            # 移除元数据
    remove_annotations: bool = False         # 移除注释
    optimize_for_web: bool = True            # Web优化
    output_file: Optional[Path] = None       # 输出文件路径

@dataclass
class CompressionResult(OperationResult):
    """压缩操作结果"""
    original_size: Optional[int] = None      # 原始文件大小
    compressed_size: Optional[int] = None    # 压缩后大小
    compression_ratio: Optional[float] = None # 压缩比例
```

#### 2. 扩展核心引擎 (`core/pdf_operations.py`)

```python
import os
from uuid import uuid4
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import io

class PDFOperations:
    """PDF操作核心引擎 - 扩展压缩功能"""
    
    def compress_pdf(self, file_path: Path, options: CompressionOptions) -> CompressionResult:
        """
        PDF压缩功能
        
        Args:
            file_path: 输入PDF文件路径
            options: 压缩选项配置
            
        Returns:
            CompressionResult: 压缩操作结果
            
        Raises:
            PDFValidationError: 文件验证失败
            PDFProcessingError: 压缩处理失败
        """
        try:
            # 1. 验证输入文件
            self.validate_pdf_file(file_path)
            logger.info(f"开始压缩PDF文件: {file_path}")
            
            # 2. 获取原始文件大小
            original_size = file_path.stat().st_size
            
            # 3. 创建输出文件路径
            output_file = options.output_file or (
                self.temp_dir / f"compressed_{uuid4().hex}.pdf"
            )
            
            # 4. 执行压缩操作
            compressed_size = self._perform_compression(
                file_path, output_file, options
            )
            
            # 5. 计算压缩比例
            compression_ratio = 1 - (compressed_size / original_size)
            
            # 6. 返回结果
            return CompressionResult(
                success=True,
                message=f"PDF压缩成功，压缩比例: {compression_ratio:.1%}",
                output_files=[output_file],
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio
            )
            
        except PDFToolError as e:
            logger.error(f"PDF压缩失败: {e}")
            return CompressionResult(
                success=False,
                message=f"PDF压缩失败: {str(e)}",
                output_files=[]
            )
        except Exception as e:
            logger.error(f"PDF压缩过程中发生未知错误: {e}")
            raise PDFProcessingError(f"PDF压缩失败: {str(e)}")
    
    def _perform_compression(
        self, 
        input_file: Path, 
        output_file: Path, 
        options: CompressionOptions
    ) -> int:
        """执行具体的压缩操作"""
        
        # 读取PDF文件
        reader = PdfReader(str(input_file))
        writer = PdfWriter()
        
        # 处理每一页
        for page_num, page in enumerate(reader.pages):
            # 压缩页面内容
            if options.compress_images:
                page = self._compress_page_images(page, options.quality)
            
            # 优化页面对象
            page.compress_content_streams()
            writer.add_page(page)
        
        # 移除元数据
        if options.remove_metadata:
            writer.add_metadata({})
        else:
            writer.add_metadata(reader.metadata or {})
        
        # 移除注释
        if options.remove_annotations:
            for page in writer.pages:
                if '/Annots' in page:
                    del page['/Annots']
        
        # 写入压缩后的文件
        with open(output_file, 'wb') as output_stream:
            writer.write(output_stream)
        
        return output_file.stat().st_size
    
    def _compress_page_images(self, page, quality: float):
        """压缩页面中的图片"""
        # 实现图片压缩逻辑
        # 这里可以添加具体的图片处理代码
        return page
```

#### 3. 添加自定义异常 (`core/exceptions.py`)

```python
class PDFCompressionError(PDFProcessingError):
    """PDF压缩专用异常"""
    pass

class InvalidCompressionQualityError(PDFValidationError):
    """无效的压缩质量参数"""
    pass
```

---

### 🌐 第三步：API层实现

#### 1. 创建服务层 (`api/services/compression_service.py`)

```python
from typing import List, Optional
from fastapi import UploadFile
from pathlib import Path
import tempfile
import os

from ...core.pdf_operations import PDFOperations
from ...core.models import CompressionOptions, CompressionResult
from ...core.exceptions import PDFCompressionError
from ...utils.logging import get_logger

logger = get_logger("api.services.compression")

class CompressionService:
    """PDF压缩服务类"""
    
    def __init__(self, pdf_operations: PDFOperations):
        self.pdf_ops = pdf_operations
    
    async def compress_pdf(
        self, 
        file: UploadFile, 
        quality: float = 0.7,
        compress_images: bool = True,
        remove_metadata: bool = False,
        remove_annotations: bool = False
    ) -> CompressionResult:
        """
        压缩PDF文件
        
        Args:
            file: 上传的PDF文件
            quality: 压缩质量 (0.1-1.0)
            compress_images: 是否压缩图片
            remove_metadata: 是否移除元数据
            remove_annotations: 是否移除注释
            
        Returns:
            CompressionResult: 压缩结果
        """
        temp_file = None
        try:
            # 1. 验证文件类型
            if not file.filename.lower().endswith('.pdf'):
                raise PDFCompressionError("只支持PDF文件格式")
            
            # 2. 验证压缩质量参数
            if not 0.1 <= quality <= 1.0:
                raise InvalidCompressionQualityError(
                    "压缩质量必须在0.1-1.0之间"
                )
            
            # 3. 保存临时文件
            temp_file = await self._save_upload_file(file)
            
            # 4. 配置压缩选项
            options = CompressionOptions(
                quality=quality,
                compress_images=compress_images,
                remove_metadata=remove_metadata,
                remove_annotations=remove_annotations
            )
            
            # 5. 执行压缩
            result = self.pdf_ops.compress_pdf(temp_file, options)
            
            logger.info(
                f"PDF压缩完成: {file.filename}, "
                f"压缩比例: {result.compression_ratio:.1%}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"PDF压缩服务出错: {e}")
            raise
        finally:
            # 清理临时文件
            if temp_file and temp_file.exists():
                temp_file.unlink()
    
    async def _save_upload_file(self, file: UploadFile) -> Path:
        """保存上传文件到临时位置"""
        suffix = Path(file.filename).suffix
        temp_file = Path(tempfile.mktemp(suffix=suffix))
        
        with open(temp_file, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        return temp_file
```

#### 2. 添加请求/响应模型 (`api/schemas/compression.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional

class PDFCompressionRequest(BaseModel):
    """PDF压缩请求模型"""
    quality: float = Field(
        default=0.7, 
        ge=0.1, 
        le=1.0, 
        description="压缩质量，取值范围0.1-1.0"
    )
    compress_images: bool = Field(
        default=True, 
        description="是否压缩图片"
    )
    remove_metadata: bool = Field(
        default=False, 
        description="是否移除文档元数据"
    )
    remove_annotations: bool = Field(
        default=False, 
        description="是否移除注释"
    )

class PDFCompressionResponse(BaseModel):
    """PDF压缩响应模型"""
    success: bool = Field(description="操作是否成功")
    message: str = Field(description="操作结果消息")
    original_size: Optional[int] = Field(description="原始文件大小(字节)")
    compressed_size: Optional[int] = Field(description="压缩后文件大小(字节)")
    compression_ratio: Optional[float] = Field(description="压缩比例(0-1)")
    savings: Optional[str] = Field(description="节省的存储空间")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "PDF压缩成功",
                "original_size": 10485760,
                "compressed_size": 5242880,
                "compression_ratio": 0.5,
                "savings": "5.0 MB"
            }
        }
```

#### 3. 添加路由端点 (`api/routers/pdf.py`)

```python
from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import Annotated

from ..services.compression_service import CompressionService
from ..schemas.compression import PDFCompressionResponse
from ..dependencies import get_compression_service
from ...utils.logging import get_logger

logger = get_logger("api.routers.pdf")

@router.post(
    "/compress",
    summary="压缩PDF文件",
    description="压缩PDF文件以减少文件大小，支持多种压缩选项",
    responses={
        200: {"description": "压缩成功，返回压缩后的PDF文件"},
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def compress_pdf(
    file: Annotated[UploadFile, File(description="要压缩的PDF文件")],
    quality: Annotated[float, Form(description="压缩质量(0.1-1.0)")] = 0.7,
    compress_images: Annotated[bool, Form(description="是否压缩图片")] = True,
    remove_metadata: Annotated[bool, Form(description="是否移除元数据")] = False,
    remove_annotations: Annotated[bool, Form(description="是否移除注释")] = False,
    compression_service: CompressionService = Depends(get_compression_service)
):
    """压缩PDF文件接口"""
    
    try:
        # 执行压缩
        result = await compression_service.compress_pdf(
            file=file,
            quality=quality,
            compress_images=compress_images,
            remove_metadata=remove_metadata,
            remove_annotations=remove_annotations
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        # 返回压缩后的文件
        output_file = result.output_files[0]
        
        return FileResponse(
            path=str(output_file),
            filename=f"compressed_{file.filename}",
            media_type="application/pdf",
            headers={
                "X-Original-Size": str(result.original_size),
                "X-Compressed-Size": str(result.compressed_size),
                "X-Compression-Ratio": str(result.compression_ratio)
            }
        )
        
    except Exception as e:
        logger.error(f"PDF压缩接口错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/compress/info",
    response_model=PDFCompressionResponse,
    summary="获取压缩功能信息"
)
async def get_compression_info():
    """获取PDF压缩功能的详细信息"""
    return PDFCompressionResponse(
        success=True,
        message="PDF压缩功能可用",
        original_size=None,
        compressed_size=None,
        compression_ratio=None,
        savings=None
    )
```

#### 4. 创建Web界面模板 (`api/templates/compress.html`)

```html
{% extends "base.html" %}

{% block title %}PDF压缩 - PDFTool{% endblock %}

{% block content %}
<div class="container">
    <div class="header">
        <h1>📉 PDF压缩</h1>
        <p>减少PDF文件大小，提高传输和存储效率</p>
    </div>

    <div class="upload-section">
        <form id="compressForm" enctype="multipart/form-data">
            <!-- 文件上传区域 -->
            <div class="file-upload" id="fileUpload">
                <div class="upload-icon">📄</div>
                <p>拖拽PDF文件到此处或点击选择</p>
                <input type="file" id="fileInput" name="file" accept=".pdf" required>
                <button type="button" onclick="document.getElementById('fileInput').click()">
                    选择PDF文件
                </button>
            </div>

            <!-- 压缩选项 -->
            <div class="options-panel" id="optionsPanel" style="display: none;">
                <h3>🔧 压缩选项</h3>
                
                <div class="option-group">
                    <label for="quality">压缩质量:</label>
                    <input type="range" id="quality" name="quality" 
                           min="0.1" max="1.0" step="0.1" value="0.7">
                    <span id="qualityValue">0.7</span>
                </div>

                <div class="option-group">
                    <label>
                        <input type="checkbox" name="compress_images" checked>
                        压缩图片
                    </label>
                </div>

                <div class="option-group">
                    <label>
                        <input type="checkbox" name="remove_metadata">
                        移除元数据
                    </label>
                </div>

                <div class="option-group">
                    <label>
                        <input type="checkbox" name="remove_annotations">
                        移除注释
                    </label>
                </div>

                <button type="submit" class="compress-btn">
                    🗜️ 开始压缩
                </button>
            </div>
        </form>
    </div>

    <!-- 结果显示区域 -->
    <div class="result-section" id="resultSection" style="display: none;">
        <h3>✅ 压缩完成</h3>
        <div class="result-info">
            <div class="size-comparison">
                <div class="size-item">
                    <span class="label">原始大小:</span>
                    <span id="originalSize">-</span>
                </div>
                <div class="size-item">
                    <span class="label">压缩后:</span>
                    <span id="compressedSize">-</span>
                </div>
                <div class="size-item highlight">
                    <span class="label">节省空间:</span>
                    <span id="savings">-</span>
                </div>
            </div>
        </div>
        <button id="downloadBtn" class="download-btn">
            📥 下载压缩文件
        </button>
    </div>

    <!-- 进度指示器 -->
    <div class="progress-section" id="progressSection" style="display: none;">
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        <p>正在压缩PDF文件，请稍候...</p>
    </div>
</div>

<script>
// JavaScript 实现文件上传和压缩处理
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const fileUpload = document.getElementById('fileUpload');
    const optionsPanel = document.getElementById('optionsPanel');
    const compressForm = document.getElementById('compressForm');
    const qualitySlider = document.getElementById('quality');
    const qualityValue = document.getElementById('qualityValue');
    
    // 质量滑块事件
    qualitySlider.addEventListener('input', function() {
        qualityValue.textContent = this.value;
    });
    
    // 文件选择事件
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            optionsPanel.style.display = 'block';
        }
    });
    
    // 拖拽支持
    fileUpload.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });
    
    fileUpload.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
    });
    
    fileUpload.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type === 'application/pdf') {
            fileInput.files = files;
            optionsPanel.style.display = 'block';
        }
    });
    
    // 表单提交事件
    compressForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const progressSection = document.getElementById('progressSection');
        const resultSection = document.getElementById('resultSection');
        
        try {
            // 显示进度
            progressSection.style.display = 'block';
            resultSection.style.display = 'none';
            
            // 提交压缩请求
            const response = await fetch('/api/v1/pdf/compress', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // 获取文件信息
                const originalSize = response.headers.get('X-Original-Size');
                const compressedSize = response.headers.get('X-Compressed-Size');
                const compressionRatio = response.headers.get('X-Compression-Ratio');
                
                // 显示结果
                showCompressionResult(originalSize, compressedSize, compressionRatio);
                
                // 准备下载
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const downloadBtn = document.getElementById('downloadBtn');
                
                downloadBtn.onclick = function() {
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `compressed_${fileInput.files[0].name}`;
                    a.click();
                };
                
            } else {
                const error = await response.text();
                throw new Error(error);
            }
            
        } catch (error) {
            alert('压缩失败: ' + error.message);
        } finally {
            progressSection.style.display = 'none';
        }
    });
    
    function showCompressionResult(originalSize, compressedSize, compressionRatio) {
        const resultSection = document.getElementById('resultSection');
        
        document.getElementById('originalSize').textContent = formatFileSize(originalSize);
        document.getElementById('compressedSize').textContent = formatFileSize(compressedSize);
        
        const savings = originalSize - compressedSize;
        document.getElementById('savings').textContent = 
            `${formatFileSize(savings)} (${(compressionRatio * 100).toFixed(1)}%)`;
        
        resultSection.style.display = 'block';
    }
    
    function formatFileSize(bytes) {
        const sizes = ['B', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 B';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
});
</script>
{% endblock %}
```

#### 5. 添加Web路由 (`api/routers/web.py`)

```python
@router.get("/compress", response_class=HTMLResponse, summary="PDF压缩页面")
async def compress_page(request: Request):
    """PDF压缩功能页面"""
    return templates.TemplateResponse("compress.html", {"request": request})
```

---

### 🖥️ 第四步：GUI层实现

#### 扩展GUI应用 (`gui/main.py`)

```python
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

class ModernPDFTool:
    """现代化PDF工具GUI - 添加压缩功能"""
    
    def create_compress_tab(self):
        """创建PDF压缩标签页"""
        compress_frame = ttk.Frame(self.notebook)
        self.notebook.add(compress_frame, text="📉 PDF压缩")
        
        # 主容器
        main_frame = ttk.Frame(compress_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="📉 PDF压缩", 
            font=("微软雅黑", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="选择PDF文件", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.compress_file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.compress_file_var, width=50)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(
            file_frame, 
            text="浏览", 
            command=self.browse_compress_file
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # 压缩选项区域
        options_frame = ttk.LabelFrame(main_frame, text="压缩选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 压缩质量
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(quality_frame, text="压缩质量:").pack(side=tk.LEFT)
        
        self.quality_var = tk.DoubleVar(value=0.7)
        quality_scale = ttk.Scale(
            quality_frame,
            from_=0.1,
            to=1.0,
            variable=self.quality_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        quality_scale.pack(side=tk.LEFT, padx=(10, 10))
        
        self.quality_label = ttk.Label(quality_frame, text="0.7")
        self.quality_label.pack(side=tk.LEFT)
        
        quality_scale.configure(command=self.update_quality_label)
        
        # 其他选项
        self.compress_images_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="压缩图片",
            variable=self.compress_images_var
        ).pack(anchor=tk.W, pady=2)
        
        self.remove_metadata_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="移除元数据",
            variable=self.remove_metadata_var
        ).pack(anchor=tk.W, pady=2)
        
        self.remove_annotations_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="移除注释",
            variable=self.remove_annotations_var
        ).pack(anchor=tk.W, pady=2)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.compress_btn = ttk.Button(
            button_frame,
            text="🗜️ 开始压缩",
            command=self.compress_pdf_action,
            style="Accent.TButton"
        )
        self.compress_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 进度条
        self.compress_progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=400
        )
        self.compress_progress.pack(pady=20, fill=tk.X)
        self.compress_progress.pack_forget()  # 初始隐藏
        
        # 结果显示区域
        self.compress_result_frame = ttk.LabelFrame(
            main_frame, 
            text="压缩结果", 
            padding="10"
        )
        # 初始隐藏结果区域
        
    def browse_compress_file(self):
        """浏览选择要压缩的PDF文件"""
        file_path = filedialog.askopenfilename(
            title="选择PDF文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.compress_file_var.set(file_path)
    
    def update_quality_label(self, value):
        """更新压缩质量标签"""
        self.quality_label.config(text=f"{float(value):.1f}")
    
    def compress_pdf_action(self):
        """执行PDF压缩操作"""
        file_path = self.compress_file_var.get()
        
        if not file_path:
            messagebox.showerror("错误", "请先选择PDF文件")
            return
        
        if not Path(file_path).exists():
            messagebox.showerror("错误", "文件不存在")
            return
        
        # 在后台线程中执行压缩
        threading.Thread(
            target=self._compress_pdf_thread,
            args=(file_path,),
            daemon=True
        ).start()
    
    def _compress_pdf_thread(self, file_path):
        """在后台线程中执行PDF压缩"""
        try:
            # 显示进度条
            self.root.after(0, self._show_compress_progress)
            
            # 配置压缩选项
            from ..core.models import CompressionOptions
            options = CompressionOptions(
                quality=self.quality_var.get(),
                compress_images=self.compress_images_var.get(),
                remove_metadata=self.remove_metadata_var.get(),
                remove_annotations=self.remove_annotations_var.get()
            )
            
            # 执行压缩
            result = self.pdf_operations.compress_pdf(Path(file_path), options)
            
            # 在主线程中显示结果
            self.root.after(0, self._show_compress_result, result)
            
        except Exception as e:
            self.root.after(0, self._show_compress_error, str(e))
    
    def _show_compress_progress(self):
        """显示压缩进度"""
        self.compress_btn.config(state='disabled')
        self.compress_progress.pack(pady=20, fill=tk.X)
        self.compress_progress.start()
    
    def _hide_compress_progress(self):
        """隐藏压缩进度"""
        self.compress_progress.stop()
        self.compress_progress.pack_forget()
        self.compress_btn.config(state='normal')
    
    def _show_compress_result(self, result):
        """显示压缩结果"""
        self._hide_compress_progress()
        
        if result.success:
            # 显示成功结果
            self.compress_result_frame.pack(fill=tk.X, pady=20)
            
            # 清空之前的内容
            for widget in self.compress_result_frame.winfo_children():
                widget.destroy()
            
            # 显示压缩统计
            stats_text = f"""压缩完成！
原始大小: {self._format_file_size(result.original_size)}
压缩后大小: {self._format_file_size(result.compressed_size)}
压缩比例: {result.compression_ratio:.1%}
节省空间: {self._format_file_size(result.original_size - result.compressed_size)}"""
            
            ttk.Label(
                self.compress_result_frame,
                text=stats_text,
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=(0, 10))
            
            # 打开文件按钮
            ttk.Button(
                self.compress_result_frame,
                text="📂 打开输出文件夹",
                command=lambda: self._open_file_location(result.output_files[0])
            ).pack(side=tk.LEFT)
            
            messagebox.showinfo("成功", f"PDF压缩成功！\n{result.message}")
        else:
            messagebox.showerror("错误", f"PDF压缩失败：\n{result.message}")
    
    def _show_compress_error(self, error_msg):
        """显示压缩错误"""
        self._hide_compress_progress()
        messagebox.showerror("错误", f"压缩过程中发生错误：\n{error_msg}")
    
    def _format_file_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _open_file_location(self, file_path):
        """打开文件所在位置"""
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            subprocess.run(["explorer", "/select,", str(file_path)])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", "-R", str(file_path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(file_path.parent)])
```

---

### ⚙️ 第五步：配置和测试

#### 1. 添加配置选项 (`config/settings.py`)

```python
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """应用配置 - 添加压缩相关配置"""
    
    # 现有配置...
    
    # PDF压缩配置
    compression_default_quality: float = Field(
        default=0.7,
        env="PDFTOOL_COMPRESSION_DEFAULT_QUALITY",
        description="默认压缩质量"
    )
    compression_min_quality: float = Field(
        default=0.1,
        env="PDFTOOL_COMPRESSION_MIN_QUALITY",
        description="最小压缩质量"
    )
    compression_max_quality: float = Field(
        default=1.0,
        env="PDFTOOL_COMPRESSION_MAX_QUALITY",
        description="最大压缩质量"
    )
    enable_image_compression: bool = Field(
        default=True,
        env="PDFTOOL_ENABLE_IMAGE_COMPRESSION",
        description="是否启用图片压缩"
    )
    compression_cache_size: int = Field(
        default=100,
        env="PDFTOOL_COMPRESSION_CACHE_SIZE",
        description="压缩缓存大小(MB)"
    )
```

#### 2. 编写单元测试 (`tests/test_compression.py`)

```python
import pytest
from pathlib import Path
import tempfile
import shutil

from src.pdftool.core.pdf_operations import PDFOperations
from src.pdftool.core.models import CompressionOptions
from src.pdftool.core.exceptions import PDFCompressionError, InvalidCompressionQualityError

class TestPDFCompression:
    """PDF压缩功能测试"""
    
    @pytest.fixture
    def pdf_operations(self):
        """PDF操作实例"""
        temp_dir = Path(tempfile.mkdtemp())
        pdf_ops = PDFOperations(temp_dir)
        yield pdf_ops
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_pdf(self):
        """示例PDF文件"""
        # 这里应该准备一个测试用的PDF文件
        return Path("tests/fixtures/sample.pdf")
    
    def test_compress_pdf_success(self, pdf_operations, sample_pdf):
        """测试PDF压缩成功"""
        options = CompressionOptions(
            quality=0.7,
            compress_images=True,
            remove_metadata=False
        )
        
        result = pdf_operations.compress_pdf(sample_pdf, options)
        
        assert result.success
        assert len(result.output_files) == 1
        assert result.output_files[0].exists()
        assert result.original_size > 0
        assert result.compressed_size > 0
        assert result.compressed_size < result.original_size
        assert 0 <= result.compression_ratio <= 1
    
    def test_compress_pdf_invalid_quality(self, pdf_operations, sample_pdf):
        """测试无效的压缩质量参数"""
        options = CompressionOptions(quality=1.5)  # 超出范围
        
        with pytest.raises(InvalidCompressionQualityError):
            pdf_operations.compress_pdf(sample_pdf, options)
    
    def test_compress_pdf_file_not_found(self, pdf_operations):
        """测试文件不存在的情况"""
        non_existent_file = Path("non_existent.pdf")
        options = CompressionOptions()
        
        result = pdf_operations.compress_pdf(non_existent_file, options)
        
        assert not result.success
        assert "文件不存在" in result.message
    
    def test_compress_pdf_different_quality_levels(self, pdf_operations, sample_pdf):
        """测试不同压缩质量级别"""
        qualities = [0.1, 0.5, 0.9]
        results = []
        
        for quality in qualities:
            options = CompressionOptions(quality=quality)
            result = pdf_operations.compress_pdf(sample_pdf, options)
            results.append(result)
        
        # 验证压缩质量越低，文件越小
        assert results[0].compressed_size <= results[1].compressed_size
        assert results[1].compressed_size <= results[2].compressed_size
    
    def test_compress_pdf_with_metadata_removal(self, pdf_operations, sample_pdf):
        """测试移除元数据的压缩"""
        options = CompressionOptions(
            quality=0.7,
            remove_metadata=True
        )
        
        result = pdf_operations.compress_pdf(sample_pdf, options)
        
        assert result.success
        # 这里可以添加验证元数据是否真正被移除的逻辑
    
    @pytest.mark.asyncio
    async def test_compression_service_api(self):
        """测试压缩服务API"""
        from src.pdftool.api.services.compression_service import CompressionService
        from fastapi import UploadFile
        import io
        
        # 模拟文件上传
        file_content = b"fake pdf content"  # 实际测试中应使用真实PDF
        upload_file = UploadFile(
            filename="test.pdf",
            file=io.BytesIO(file_content)
        )
        
        pdf_ops = PDFOperations()
        service = CompressionService(pdf_ops)
        
        # 这个测试需要真实的PDF文件才能正常工作
        # 在实际环境中，应该使用真实的PDF文件进行测试
```

#### 3. 集成测试 (`tests/test_compression_integration.py`)

```python
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

from src.pdftool.api.app import create_app

class TestCompressionIntegration:
    """PDF压缩功能集成测试"""
    
    @pytest.fixture
    def client(self):
        """测试客户端"""
        app = create_app()
        return TestClient(app)
    
    @pytest.fixture
    def sample_pdf_file(self):
        """示例PDF文件用于上传测试"""
        # 准备测试用PDF文件
        return ("test.pdf", open("tests/fixtures/sample.pdf", "rb"), "application/pdf")
    
    def test_compress_pdf_api_endpoint(self, client, sample_pdf_file):
        """测试PDF压缩API端点"""
        response = client.post(
            "/api/v1/pdf/compress",
            files={"file": sample_pdf_file},
            data={
                "quality": 0.7,
                "compress_images": True,
                "remove_metadata": False
            }
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "X-Original-Size" in response.headers
        assert "X-Compressed-Size" in response.headers
        assert "X-Compression-Ratio" in response.headers
    
    def test_compress_pdf_web_page(self, client):
        """测试PDF压缩Web页面"""
        response = client.get("/compress")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "PDF压缩" in response.text
    
    def test_compress_pdf_invalid_file(self, client):
        """测试上传无效文件"""
        fake_file = ("test.txt", io.BytesIO(b"not a pdf"), "text/plain")
        
        response = client.post(
            "/api/v1/pdf/compress",
            files={"file": fake_file},
            data={"quality": 0.7}
        )
        
        assert response.status_code == 400
    
    def test_compress_pdf_invalid_quality(self, client, sample_pdf_file):
        """测试无效的压缩质量参数"""
        response = client.post(
            "/api/v1/pdf/compress",
            files={"file": sample_pdf_file},
            data={"quality": 1.5}  # 超出范围
        )
        
        assert response.status_code == 422  # Validation error
```

#### 4. 更新依赖 (`requirements.txt`)

```txt
# 现有依赖...

# PDF压缩额外依赖
Pillow>=9.0.0          # 图片处理
reportlab>=3.6.0       # PDF生成和处理增强
```

#### 5. 更新文档和示例

在主页面的功能选择卡片中添加压缩功能：

```html
<!-- api/templates/index.html 更新 -->
<div class="function-card" onclick="goToFunction('compress')">
    <div class="card-icon">🗜️</div>
    <h3>PDF压缩</h3>
    <p>减少PDF文件大小，支持多种压缩选项</p>
    <div class="card-features">
        <span>• 智能压缩</span>
        <span>• 质量可调</span>
        <span>• 批量处理</span>
    </div>
</div>
```

---

### 🔄 第六步：验证和部署

#### 1. 功能验证清单

```markdown
- [ ] 核心压缩引擎功能正常
- [ ] API端点响应正确
- [ ] Web界面交互流畅
- [ ] GUI应用功能完整
- [ ] 单元测试全部通过
- [ ] 集成测试验证通过
- [ ] 性能测试满足要求
- [ ] 错误处理覆盖完整
- [ ] 文档更新同步
- [ ] 配置项正确设置
```

#### 2. 性能测试

```python
# tests/test_compression_performance.py
import time
import pytest
from pathlib import Path

def test_compression_performance():
    """测试压缩性能"""
    large_pdf = Path("tests/fixtures/large_sample.pdf")  # 10MB+ PDF
    pdf_ops = PDFOperations()
    
    start_time = time.time()
    result = pdf_ops.compress_pdf(large_pdf, CompressionOptions(quality=0.7))
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    assert result.success
    assert processing_time < 30  # 应在30秒内完成
    assert result.compression_ratio > 0.1  # 至少压缩10%
```

#### 3. 部署更新

更新 `Makefile` 添加压缩功能相关命令：

```makefile
# 压缩功能测试
test-compression:
	pytest tests/test_compression*.py -v

# 压缩性能测试
test-compression-perf:
	pytest tests/test_compression_performance.py -v --benchmark

# 构建包含压缩功能的镜像
docker-build-with-compression:
	docker build -t pdftool:compression-enabled .
```

---

### 🚀 总结

通过以上详细步骤，我们成功为PDFTool添加了完整的PDF压缩功能：

1. **核心层**: 实现了`compress_pdf`方法和相关数据模型
2. **API层**: 创建了服务类、路由端点和Web界面  
3. **GUI层**: 添加了压缩功能标签页和用户界面
4. **配置**: 增加了压缩相关的配置选项
5. **测试**: 编写了完整的单元测试和集成测试
6. **文档**: 更新了相关文档和使用说明

这个扩展开发流程可以作为添加其他新功能（如PDF水印、OCR识别、格式转换等）的标准模板。每个新功能都应该遵循相同的分层架构和开发规范，确保代码的一致性和可维护性。

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