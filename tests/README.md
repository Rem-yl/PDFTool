# PDFTool API 测试套件

本目录包含了 PDFTool API 的完整测试套件，使用 pytest 进行测试。

## 测试文件结构

```
tests/
├── conftest.py                 # 测试配置和fixtures
├── test_simple.py              # 基础环境验证测试
├── test_health.py              # 健康检查端点测试
├── test_pdf_operations.py      # PDF操作API测试
├── test_web_interface.py       # Web界面端点测试
├── test_error_handling.py      # 错误处理和边界测试
├── test_integration.py         # 集成测试和工作流程测试
└── README.md                   # 本文件
```

## 测试覆盖的API端点

### PDF操作API (/pdf/)
- `POST /pdf/info` - 获取PDF信息
- `POST /pdf/merge` - 合并PDF文件
- `POST /pdf/pages` - 页面选择/分割
- `POST /pdf/watermark` - 添加水印
- `POST /pdf/password` - 密码保护
- `POST /pdf/convert` - 格式转换
- `GET /pdf/services` - 服务列表

### Web界面 (/)
- `GET /` - 主页
- `GET /merge` - 合并页面
- `GET /info` - 信息页面
- `GET /watermark` - 水印页面
- `GET /convert` - 转换页面
- `GET /password` - 密码保护页面
- `GET /pages` - 页面选择页面

### 系统API
- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /redoc` - ReDoc文档
- `GET /openapi.json` - OpenAPI规范

## 运行测试

### 基础环境测试
```bash
# 运行基础环境验证测试
python -m pytest tests/test_simple.py -v
```

### 运行所有测试
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_health.py -v

# 运行特定测试
python -m pytest tests/test_health.py::test_health_check -v
```

### 测试覆盖率
```bash
# 生成测试覆盖率报告
python -m pytest tests/ -v --cov=src/pdftool --cov-report=html --cov-report=term
```

## 测试特点

### 全面的API测试
- **正常流程测试**: 验证API在正常情况下的行为
- **错误处理测试**: 测试各种错误情况和边界条件
- **参数验证测试**: 验证输入参数的校验逻辑
- **文件格式测试**: 测试不同文件格式的处理

### 测试数据管理
- **自动生成测试PDF**: 使用PyPDF2自动创建测试用PDF文件
- **临时文件管理**: 使用temporary directory管理测试文件
- **多种测试场景**: 包括空文件、大文件、格式错误文件等

### 集成测试
- **完整工作流程**: 测试端到端的处理流程
- **服务集成**: 验证各个服务之间的集成
- **错误恢复**: 测试服务在错误后的恢复能力

## 测试配置

### Fixtures
- `client`: HTTP测试客户端
- `temp_dir`: 临时目录
- `sample_pdf_file`: 单个测试PDF文件
- `sample_pdf_files`: 多个测试PDF文件
- `sample_image_file`: 测试图片文件

### 环境设置
- 自动设置测试环境变量
- 启用调试模式
- 配置日志级别

## 注意事项

### 版本兼容性
- 当前测试套件处理了FastAPI TestClient的版本兼容性问题
- 使用httpx进行HTTP客户端测试
- 支持PyPDF2和新版本库的迁移警告

### 测试稳定性
- 部分转换测试可能因为空白PDF而失败，这是正常的
- 大文件测试根据系统配置可能返回不同状态码
- 并发测试在某些环境下可能不稳定

### 扩展性
- 测试结构支持轻松添加新的API端点测试
- 模块化设计便于维护和扩展
- 清晰的错误消息和断言便于调试

## 最佳实践

1. **运行测试前**: 确保所有依赖都已安装
2. **测试隔离**: 每个测试都是独立的，使用独立的临时文件
3. **错误处理**: 测试包含了各种边界情况和错误场景
4. **文档更新**: 添加新API时记得更新对应的测试
5. **持续集成**: 建议在CI/CD流水线中运行这些测试

## 故障排除

### 常见问题
1. **TestClient导入错误**: 已通过使用httpx解决
2. **PDF生成失败**: 检查PyPDF2版本和依赖
3. **文件权限问题**: 确保有临时目录的读写权限
4. **端口冲突**: 测试使用内存传输，不会有端口冲突

### 调试技巧
```bash
# 增加详细输出
python -m pytest tests/ -v -s

# 停在第一个失败
python -m pytest tests/ -x

# 运行特定标记的测试
python -m pytest tests/ -m "not slow"
```