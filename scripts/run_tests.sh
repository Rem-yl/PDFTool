#!/bin/bash
#
# PDFTool 测试运行脚本 (Shell版本)
# 快速一键运行测试的shell脚本
#

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
PDFTool 测试运行脚本

用法: $0 [选项]

选项:
    -h, --help          显示此帮助信息
    -q, --quick         快速模式，只运行基础测试
    -c, --coverage      生成覆盖率报告
    -l, --lint          只运行代码检查
    -f, --fix           运行代码格式化
    --clean             清理测试文件
    --install-deps      安装测试依赖
    --pre-commit        Pre-commit模式（用于git hook）

示例:
    $0                  # 运行完整测试套件
    $0 -q               # 快速测试
    $0 -c               # 带覆盖率的完整测试
    $0 -l               # 只运行代码检查
    $0 --clean          # 清理测试文件
EOF
}

# 检查依赖
check_dependencies() {
    log_info "检查测试依赖..."

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        return 1
    fi

    # 检查pytest
    if ! python3 -c "import pytest" 2>/dev/null; then
        log_error "pytest 未安装，请运行: pip install pytest"
        return 1
    fi

    log_success "依赖检查通过"
    return 0
}

# 安装依赖
install_dependencies() {
    log_info "安装测试依赖..."

    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        python3 -m pip install -r "$PROJECT_ROOT/requirements.txt"
        log_success "依赖安装完成"
    else
        log_warning "requirements.txt 文件不存在，尝试安装基础依赖"
        python3 -m pip install pytest pytest-cov pytest-asyncio httpx fastapi PyPDF2 Pillow
    fi
}

# 设置环境变量
setup_environment() {
    export PDFTOOL_DEBUG="true"
    export PDFTOOL_LOG_LEVEL="DEBUG"
    export PDFTOOL_TEMP_DIR="temp_test"
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

    log_success "测试环境设置完成"
}

# 代码检查
run_lint() {
    log_info "运行代码检查..."

    cd "$PROJECT_ROOT"

    # flake8 检查
    if command -v flake8 &> /dev/null; then
        log_info "运行 flake8..."
        if ! flake8 src/ --max-line-length=100 --extend-ignore=E203,W503; then
            log_error "flake8 检查失败"
            return 1
        fi
    else
        log_warning "flake8 未安装，跳过"
    fi

    # mypy 检查
    if command -v mypy &> /dev/null; then
        log_info "运行 mypy..."
        if ! mypy src/ --ignore-missing-imports; then
            log_error "mypy 检查失败"
            return 1
        fi
    else
        log_warning "mypy 未安装，跳过"
    fi

    log_success "代码检查通过"
    return 0
}

# 代码格式化
run_format() {
    log_info "运行代码格式化..."

    cd "$PROJECT_ROOT"

    # black 格式化
    if command -v black &> /dev/null; then
        log_info "运行 black..."
        black src/ tests/ --line-length=100
        log_success "black 格式化完成"
    else
        log_warning "black 未安装，跳过格式化"
    fi

    # isort 格式化
    if command -v isort &> /dev/null; then
        log_info "运行 isort..."
        isort src/ tests/
        log_success "isort 格式化完成"
    else
        log_warning "isort 未安装，跳过导入排序"
    fi
}

# 运行基础测试
run_basic_tests() {
    log_info "运行基础测试..."

    cd "$PROJECT_ROOT"

    if python3 -m pytest tests/test_simple.py -v --tb=short; then
        log_success "基础测试通过"
        return 0
    else
        log_error "基础测试失败"
        return 1
    fi
}

# 运行完整测试
run_full_tests() {
    log_info "运行完整测试套件..."

    cd "$PROJECT_ROOT"

    local pytest_args="tests/ -v --tb=short"

    if [ "$COVERAGE" = "true" ]; then
        pytest_args="$pytest_args --cov=src/pdftool --cov-report=term-missing --cov-report=html:htmlcov"
    fi

    if python3 -m pytest $pytest_args; then
        log_success "完整测试通过"
        if [ "$COVERAGE" = "true" ]; then
            log_info "覆盖率报告已生成: htmlcov/index.html"
        fi
        return 0
    else
        log_error "测试失败"
        return 1
    fi
}

# 清理测试文件
cleanup() {
    log_info "清理测试文件..."

    cd "$PROJECT_ROOT"

    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true

    # 清理pytest缓存
    rm -rf .pytest_cache 2>/dev/null || true

    # 清理覆盖率文件
    rm -f .coverage 2>/dev/null || true

    # 清理临时目录
    rm -rf temp_test 2>/dev/null || true

    log_success "清理完成"
}

# Pre-commit模式
run_pre_commit() {
    log_info "运行 Pre-commit 检查..."

    # 只运行基础测试和代码检查，快速失败
    if ! run_lint; then
        log_error "代码检查失败，阻止提交"
        return 1
    fi

    if ! run_basic_tests; then
        log_error "基础测试失败，阻止提交"
        return 1
    fi

    log_success "Pre-commit 检查通过，允许提交"
    return 0
}

# 主函数
main() {
    local QUICK_MODE=false
    local COVERAGE=false
    local LINT_ONLY=false
    local FORMAT_ONLY=false
    local CLEAN_ONLY=false
    local INSTALL_DEPS=false
    local PRE_COMMIT_MODE=false

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -q|--quick)
                QUICK_MODE=true
                shift
                ;;
            -c|--coverage)
                COVERAGE=true
                shift
                ;;
            -l|--lint)
                LINT_ONLY=true
                shift
                ;;
            -f|--fix)
                FORMAT_ONLY=true
                shift
                ;;
            --clean)
                CLEAN_ONLY=true
                shift
                ;;
            --install-deps)
                INSTALL_DEPS=true
                shift
                ;;
            --pre-commit)
                PRE_COMMIT_MODE=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 显示启动信息
    log_info "PDFTool 测试运行器启动"
    log_info "项目根目录: $PROJECT_ROOT"

    # 处理特殊模式
    if [ "$CLEAN_ONLY" = "true" ]; then
        cleanup
        exit 0
    fi

    if [ "$INSTALL_DEPS" = "true" ]; then
        install_dependencies
        exit 0
    fi

    if [ "$FORMAT_ONLY" = "true" ]; then
        run_format
        exit 0
    fi

    # 检查依赖
    if ! check_dependencies; then
        log_error "依赖检查失败"
        exit 1
    fi

    # 设置环境
    setup_environment

    # 根据模式运行测试
    if [ "$PRE_COMMIT_MODE" = "true" ]; then
        if run_pre_commit; then
            exit 0
        else
            exit 1
        fi
    elif [ "$LINT_ONLY" = "true" ]; then
        if run_lint; then
            exit 0
        else
            exit 1
        fi
    elif [ "$QUICK_MODE" = "true" ]; then
        if run_basic_tests; then
            exit 0
        else
            exit 1
        fi
    else
        # 完整测试流程
        local success=true

        # 代码检查（非致命）
        if ! run_lint; then
            log_warning "代码检查失败，但继续运行测试..."
        fi

        # 基础测试
        if ! run_basic_tests; then
            log_error "基础测试失败，跳过完整测试"
            exit 1
        fi

        # 完整测试
        if ! run_full_tests; then
            success=false
        fi

        # 清理
        cleanup

        if [ "$success" = "true" ]; then
            log_success "🎉 所有测试通过!"
            exit 0
        else
            log_error "💥 测试失败!"
            exit 1
        fi
    fi
}

# 运行主函数
main "$@"