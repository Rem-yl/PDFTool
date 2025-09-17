# VS Code 调试配置说明

这个目录包含VS Code的调试配置文件，用于调试PDFTool项目的各个组件。

## 文件说明

- `launch.json` - VS Code调试配置文件

## 调试配置列表

### 1. Debug FastAPI App
**推荐用于生产环境调试**
- 通过 `pdftool.api.main` 模块启动
- 使用项目的main.py入口点
- 包含完整的应用初始化流程

### 2. Debug FastAPI with Uvicorn
**推荐用于开发调试**
- 使用Uvicorn服务器启动
- 支持热重载 (`--reload`)
- 代码更改时自动重启
- 最适合日常开发使用

### 3. Debug FastAPI App Direct
**快速调试选项**
- 直接启动FastAPI app实例
- 绕过main.py的启动逻辑
- 用于快速测试API端点

### 4. Debug GUI App
- 调试桌面GUI应用
- 启动Tkinter界面
- 用于GUI功能开发和调试

### 5. Debug Tests
- 运行并调试所有测试
- 使用pytest框架
- 显示详细的测试输出

### 6. Debug Current File
- 调试当前打开的Python文件
- 通用调试配置
- 适用于单独的脚本文件

## 如何使用

### 方法一：使用调试面板
1. 打开VS Code调试面板 (Ctrl+Shift+D / Cmd+Shift+D)
2. 从下拉菜单选择调试配置
3. 点击绿色播放按钮开始调试

### 方法二：使用快捷键
1. 按 F5 启动调试
2. 如果有多个配置，VS Code会提示选择

### 方法三：使用命令面板
1. 打开命令面板 (Ctrl+Shift+P / Cmd+Shift+P)
2. 输入 "Debug: Start Debugging"
3. 选择调试配置

## 环境变量配置

所有调试配置都包含以下环境变量：

```json
{
    "PYTHONPATH": "${workspaceFolder}/src",
    "PDFTOOL_DEBUG": "true",
    "PDFTOOL_LOG_LEVEL": "DEBUG"
}
```

- `PYTHONPATH`: 确保Python能找到项目模块
- `PDFTOOL_DEBUG`: 启用调试模式
- `PDFTOOL_LOG_LEVEL`: 设置详细日志输出

## 断点调试

### 设置断点
- 在代码行号左侧点击红点设置断点
- 或者在代码行按 F9 切换断点

### 调试控制
- **F5**: 继续执行
- **F10**: 单步跳过 (Step Over)
- **F11**: 单步进入 (Step Into)
- **Shift+F11**: 单步跳出 (Step Out)
- **Ctrl+Shift+F5**: 重新启动调试

### 调试面板功能
- **变量**: 查看当前作用域的变量值
- **监视**: 添加自定义表达式监视
- **调用堆栈**: 查看函数调用链
- **断点**: 管理所有断点

## 常见问题

### Q: 相对导入错误
A: 确保使用模块方式启动 (`"module": "pdftool.api.main"`)，而不是直接指定文件路径

### Q: 模块找不到
A: 检查 `PYTHONPATH` 是否正确设置为 `${workspaceFolder}/src`

### Q: 环境变量不生效
A: 确保项目根目录有 `.env` 文件，或者检查launch.json中的env配置

### Q: 热重载不工作
A: 使用 "Debug FastAPI with Uvicorn" 配置，确保有 `--reload` 参数

## 推荐调试流程

### API开发
1. 使用 "Debug FastAPI with Uvicorn"
2. 在浏览器打开 http://localhost:8000
3. 设置断点在API处理函数中
4. 通过Web界面或API客户端发送请求

### 前端调试
1. 启动API服务器
2. 在浏览器打开 http://localhost:8000
3. 使用浏览器开发者工具调试JavaScript
4. 在Python代码中设置断点调试后端逻辑

### 测试调试
1. 使用 "Debug Tests" 配置
2. 在测试代码中设置断点
3. 查看测试执行过程和变量状态

## 项目结构说明

```
src/pdftool/
├── api/           # FastAPI Web服务
├── core/          # 核心业务逻辑
├── gui/           # 桌面GUI应用
├── config/        # 配置管理
└── utils/         # 工具函数
```

调试时可以在任何模块中设置断点，调试器会自动处理模块间的调用关系。