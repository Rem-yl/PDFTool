# PDFTool

![PDFTool Logo](https://img.shields.io/badge/PDFTool-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

PDFTool 是一个现代化的 PDF 操作工具，提供 GUI 桌面应用、Web API 和命令行接口。支持 PDF 合并、拆分、信息提取等功能，采用工程化的架构设计，便于扩展和维护。

## ✨ 功能特性

### 🔧 核心功能
- **PDF 合并**: 支持多个 PDF 文件合并为一个文件
- **PDF 拆分**: 支持将 PDF 文件拆分为单页或指定页面范围
- **PDF 信息**: 获取 PDF 文件的详细信息（页数、标题、作者等）

### 🎯 多种界面
- **现代化 GUI**: 基于 Tkinter 的桌面应用，支持拖拽操作
- **Web 界面**: 提供直观的 Web 操作界面，响应式设计
- **RESTful API**: 提供完整的 API 接口，方便集成到其他系统

### 🏗️ 工程化特性
- **模块化架构**: 清晰的代码组织结构
- **类型安全**: 完整的类型注解支持
- **错误处理**: 专门的异常类型和错误处理
- **配置管理**: 环境变量和配置文件支持
- **日志系统**: 结构化日志记录
- **测试覆盖**: 完整的单元测试
- **Docker 支持**: 容器化部署

## 🚀 快速开始

### 方式一：直接安装

```bash
# 克隆项目
git clone git@github.com:Rem-yl/PDFTool.git
cd pdftool

# 安装依赖
pip install -e .

# 启动 GUI 应用
pdftool-gui

# 或启动 API 服务
pdftool-api
```

### 方式二：开发模式

```bash
# 安装开发依赖
pip install -e ".[dev,api]"

# 使用 Makefile 命令
make install-dev
make run-gui      # 启动 GUI
make run-api      # 启动 API
make test         # 运行测试
```

### 方式三：Docker 部署

```bash
# 构建并运行
docker-compose up --build

# 或使用 Makefile
make docker-build
make docker-run
```

## 📱 使用界面

### GUI 应用
启动后将看到现代化的桌面界面，支持标签页操作：
- PDF 合并标签：选择多个文件进行合并
- PDF 拆分标签：选择文件和拆分方式
- PDF 信息标签：查看文件详细信息

### Web 界面
访问 `http://localhost:8000` 使用 Web 界面：
- 响应式设计，支持移动设备
- 拖拽上传文件
- 实时操作反馈
- 进度指示器

### API 接口
访问 `http://localhost:8000/docs` 查看 Swagger 文档

## 🏗️ 项目架构

PDFTool 采用现代化的分层架构设计，具有出色的可扩展性和可维护性：

```
┌─────────────────────────────────────────┐
│           用户界面层 (UI Layer)            │
├─────────────────┬───────────┬───────────┤
│   GUI (Tkinter) │ Web UI    │  REST API │
│                 │(HTML/JS)  │   (v1)    │
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
│         服务层 (Service Layer)           │
├─────────────────────────────────────────┤
│   PDF Service │ File Service │ Utils   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│          核心层 (Core Layer)             │
├─────────────────────────────────────────┤
│     PDFOperations (PyPDF2引擎)          │
└─────────────────────────────────────────┘
```

详细架构说明请参考 → **[完整架构文档](./WIKI.md)**

## 🔧 API 接口

PDFTool 提供现代化的 RESTful API，支持版本控制和完整的错误处理。

### 🌐 Web 界面端点
- `GET /` - 功能选择主页面
- `GET /merge` - PDF 合并操作页面  
- `GET /split` - PDF 拆分操作页面
- `GET /info` - PDF 信息查看页面

### 📡 API v1 端点

#### 1. PDF 合并
```http
POST /api/v1/pdf/merge
Content-Type: multipart/form-data

files: [file1.pdf, file2.pdf, ...]
preserve_bookmarks: true (可选)
preserve_metadata: true (可选)
```

#### 2. PDF 拆分
```http
POST /api/v1/pdf/split
Content-Type: multipart/form-data

file: example.pdf
mode: "all" | "range"
start_page: 1 (range模式必需)
end_page: 10 (可选)
```

#### 3. PDF 信息提取
```http
POST /api/v1/pdf/info
Content-Type: multipart/form-data

file: example.pdf
```

#### 4. 支持格式查询
```http
GET /api/v1/pdf/formats
```

### 🔍 系统监控端点
- `GET /health` - 健康检查
- `GET /health/ping` - 连通性检查
- `GET /api/version` - API版本信息
- `GET /api/endpoints` - 端点列表
- `GET /api/status` - 系统状态

### 📚 API 文档
- 开发环境: `http://localhost:8000/api/docs` (Swagger UI)
- 备用文档: `http://localhost:8000/api/redoc` (ReDoc)

## ⚙️ 配置选项

通过环境变量或 `.env` 文件配置：

```bash
# 应用设置
PDFTOOL_APP_NAME=PDFTool
PDFTOOL_DEBUG=false

# 文件处理
PDFTOOL_TEMP_DIR=temp
PDFTOOL_MAX_FILE_SIZE=104857600  # 100MB

# API 设置
PDFTOOL_API_HOST=0.0.0.0
PDFTOOL_API_PORT=8000

# 日志设置
PDFTOOL_LOG_LEVEL=INFO
PDFTOOL_LOG_FILE=logs/pdftool.log
```

## 🧪 开发和测试

### 运行测试
```bash
# 运行所有测试
make test

# 运行测试并生成覆盖率报告
make test-cov

# 代码质量检查
make lint

# 代码格式化
make format
```

### 开发命令
```bash
# 安装开发环境
make install-dev

# 启动开发服务器（支持热重载）
make dev-api

# 构建项目
make build

# 清理构建文件
make clean
```

## 📦 部署方式

### 传统部署
```bash
# 安装生产环境
pip install .
pdftool-api
```

### Docker 部署
```bash
# 单容器运行
docker run -p 8000:8000 pdftool:latest

# 使用 docker-compose（推荐）
docker-compose up -d
```

### 生产环境建议
- 使用反向代理（nginx）
- 配置 HTTPS
- 设置日志轮转
- 监控和健康检查
- 资源限制

## 🔄 从旧版本迁移

如果你使用的是旧版本的 PDFTool，请参考 [MIGRATION.md](MIGRATION.md) 获取详细的迁移指南。

主要变化：
- 新的模块化架构
- 改进的错误处理
- 配置管理系统
- 类型安全支持

## 📈 性能优化

- 异步文件处理
- 内存优化的 PDF 操作
- 临时文件自动清理
- 请求限流保护
- Docker 多阶段构建

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范
- 使用 black 进行代码格式化
- 通过 flake8 和 mypy 检查
- 编写测试用例
- 更新文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持和反馈

- 📧 邮箱: contact@pdftool.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/pdftool/pdftool/issues)
- 📖 文档: [项目文档](https://pdftool.readthedocs.io)
- 💬 讨论: [GitHub Discussions](https://github.com/pdftool/pdftool/discussions)

## 📋 开发路线图 (TODO)
- [Jira面板](https://yuleirem123.atlassian.net/jira/software/projects/PDF/boards/34)

### 🔧 代码质量优化
- [ ] 修复代码质量问题（尾随空格、导入顺序）
- [ ] 添加更多单元测试覆盖
- [ ] 性能优化和内存使用改进
- [ ] 添加代码文档和类型注解完善

### 🚀 核心功能扩展
- [ ] **PDF 压缩功能** - 减少 PDF 文件大小，支持多种压缩级别
- [ ] **PDF 水印功能** - 添加文字或图片水印到 PDF，支持透明度和位置调整
- [ ] **PDF 密码保护** - 为 PDF 文件添加/移除密码保护，支持用户密码和所有者密码
- [ ] **PDF 解密功能** - 解密受密码保护的 PDF 文件
- [ ] **PDF 旋转功能** - 旋转 PDF 页面方向（90°/180°/270°）
- [ ] **PDF 页面删除** - 删除 PDF 中的指定页面
- [ ] **PDF 页面重排** - 重新排列 PDF 页面顺序
- [ ] **PDF 页面提取** - 提取特定页面为新的 PDF 文件
- [ ] **PDF 页面插入** - 在指定位置插入新页面
- [ ] **PDF 文档修复** - 修复损坏的 PDF 文件
- [ ] **PDF 优化** - 优化 PDF 结构以提高性能
- [ ] **PDF 版本转换** - 在不同 PDF 版本间转换
- [ ] **PDF 线性化** - 创建适合网络快速查看的线性化 PDF
- [ ] **PDF 数字签名** - 为 PDF 添加数字签名和验证
- [ ] **PDF 注释处理** - 添加、编辑、删除 PDF 注释和批注

### 🎯 高级功能
- [ ] **PDF 转图片** - 将 PDF 页面转换为 PNG/JPEG/TIFF 格式，支持 DPI 设置
- [ ] **图片转 PDF** - 将多张图片合并为 PDF，支持自动排版和大小调整
- [ ] **PDF 表单处理** - 提取和填写 PDF 表单字段，支持各种表单元素
- [ ] **PDF 书签管理** - 添加、编辑、删除 PDF 书签，支持多级书签结构
- [ ] **PDF 元数据编辑** - 修改 PDF 标题、作者、主题、关键词等信息
- [ ] **PDF 文本提取** - 提取 PDF 中的所有文本内容，支持保留格式
- [ ] **PDF 文本搜索** - 在 PDF 中搜索和高亮显示文本
- [ ] **PDF 文本替换** - 查找并替换 PDF 中的文本内容
- [ ] **PDF 图片提取** - 提取 PDF 中的所有图片资源
- [ ] **PDF 字体信息** - 分析和显示 PDF 中使用的字体信息
- [ ] **PDF 结构分析** - 分析 PDF 的内部结构和对象
- [ ] **PDF 链接处理** - 添加、编辑、删除 PDF 中的超链接
- [ ] **PDF 页面缩放** - 调整 PDF 页面的缩放比例
- [ ] **PDF 页面裁剪** - 裁剪 PDF 页面的边距和内容区域
- [ ] **PDF OCR 识别** - 对扫描版 PDF 进行 OCR 文字识别
- [ ] **PDF 转 Word/Excel** - 将 PDF 转换为可编辑的 Office 文档
- [ ] **Office 转 PDF** - 将 Word/Excel/PPT 转换为 PDF
- [ ] **PDF 转 HTML** - 将 PDF 转换为 HTML 网页格式
- [ ] **HTML 转 PDF** - 将网页转换为 PDF 文档

### ⚡ 批处理和自动化
- [ ] **批处理模式** - 批量处理多个 PDF 文件，支持不同操作的组合
- [ ] **文件夹监控** - 自动监控指定文件夹，处理新增的 PDF 文件
- [ ] **任务队列系统** - 异步处理大量文件，支持优先级和重试机制
- [ ] **进度跟踪** - 大文件处理进度实时显示，支持暂停和恢复
- [ ] **定时任务** - 定期执行 PDF 处理任务，支持 cron 表达式
- [ ] **工作流编辑器** - 可视化创建复杂的 PDF 处理流程
- [ ] **条件处理** - 根据文件属性执行不同的处理逻辑
- [ ] **错误恢复** - 处理失败时的自动重试和错误处理
- [ ] **批量重命名** - 根据 PDF 内容或元数据批量重命名文件
- [ ] **文件分类** - 根据内容自动分类和整理 PDF 文件
- [ ] **模板引擎** - 创建可重用的处理模板和配置
- [ ] **导入导出配置** - 保存和分享处理配置

### 🖥️ 界面和交互
- [ ] **命令行界面 (CLI)** - 提供完整的命令行工具，支持管道操作
- [ ] **拖拽支持增强** - 改进 GUI 的拖拽体验，支持多文件和文件夹
- [ ] **预览功能** - 在处理前预览 PDF 内容，支持缩略图和页面预览
- [ ] **历史记录** - 保存和管理处理历史，支持收藏和标签
- [ ] **快捷键支持** - 为常用操作添加键盘快捷键，支持自定义
- [ ] **主题切换** - 支持暗色模式和多种界面主题
- [ ] **多语言支持** - 界面国际化，支持中英文等多种语言
- [ ] **无障碍访问** - 支持屏幕阅读器和无障碍操作
- [ ] **响应式布局** - 自适应不同屏幕尺寸和分辨率
- [ ] **实时协作** - 多用户同时编辑和协作处理
- [ ] **文件对比** - 可视化比较两个 PDF 文件的差异
- [ ] **全屏模式** - 支持全屏查看和处理模式
- [ ] **分屏显示** - 支持同时查看多个 PDF 文件
- [ ] **手势操作** - 支持触控板和触屏手势操作

### 🔌 集成和扩展
- [ ] **插件系统** - 支持第三方功能扩展，提供插件开发 SDK
- [ ] **云存储集成** - 支持 Google Drive、Dropbox、OneDrive、AWS S3 等
- [ ] **数据库支持** - 文件处理记录和用户管理，支持 MySQL/PostgreSQL/MongoDB
- [ ] **API 认证** - 添加用户认证和权限管理，支持 OAuth2 和 JWT
- [ ] **Webhook 支持** - 处理完成后的回调通知，支持自定义事件
- [ ] **第三方服务集成** - 集成 Zapier、IFTTT 等自动化平台
- [ ] **邮件集成** - 处理结果通过邮件发送，支持 SMTP 和邮件服务商
- [ ] **消息队列支持** - 集成 Redis、RabbitMQ 等消息队列系统
- [ ] **版本控制集成** - 与 Git 等版本控制系统集成
- [ ] **CI/CD 集成** - 集成到持续集成和部署流程中
- [ ] **Docker 生态** - 支持 Docker Compose 和 Kubernetes 部署
- [ ] **微服务架构** - 支持拆分为多个独立的微服务
- [ ] **GraphQL API** - 提供 GraphQL 接口支持
- [ ] **WebSocket 支持** - 实时通信和状态更新

### 📱 跨平台支持
- [ ] **移动端适配** - 改进移动设备上的 Web 界面
- [ ] **PWA 支持** - 将 Web 应用转为 PWA
- [ ] **桌面应用打包** - 使用 PyInstaller 打包桌面版
- [ ] **macOS 原生支持** - 优化 macOS 平台体验
- [ ] **Linux 发行版支持** - 为主流 Linux 发行版制作安装包

### 🔒 安全和稳定性
- [ ] **输入验证增强** - 更严格的文件格式和内容验证
- [ ] **病毒扫描集成** - 上传文件安全检查
- [ ] **访问日志** - 详细的操作审计日志
- [ ] **备份和恢复** - 数据备份和灾难恢复
- [ ] **资源限制** - CPU 和内存使用限制

### 📊 监控和分析
- [ ] **使用统计** - 功能使用情况统计
- [ ] **性能监控** - 系统性能和响应时间监控
- [ ] **错误追踪** - 集成 Sentry 等错误追踪服务
- [ ] **用户分析** - 用户行为和偏好分析

## ⭐ 致谢

感谢以下开源项目：
- [PyPDF2](https://github.com/py-pdf/PyPDF2) - PDF 处理核心
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI 框架

---

**PDFTool** - 让 PDF 操作更简单、更高效！ 🚀