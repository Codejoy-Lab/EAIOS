#!/bin/bash

# EAIOS 前后端服务管理脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装"
        exit 1
    fi

    print_success "依赖检查完成"
}

# 启动后端
start_backend() {
    print_info "启动后端服务..."

    if [ ! -f "backend/.env" ]; then
        print_warn "未找到 .env 文件，创建默认配置..."
        cp backend/.env.example backend/.env
        print_warn "请编辑 backend/.env 并设置 OPENAI_API_KEY"
    fi

    cd backend

    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建虚拟环境..."
        python3 -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    print_info "安装依赖..."
    pip install -q -r requirements.txt

    print_success "后端已启动在 http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
    echo "  健康检查: http://localhost:8000/api/health"
    echo ""

    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# 启动前端
start_frontend() {
    print_info "启动前端服务..."

    cd frontend

    if [ ! -d "node_modules" ]; then
        print_info "安装npm依赖..."
        npm install -q
    fi

    print_success "前端已启动在 http://localhost:5173"
    echo ""

    npm run dev
}

# 同时启动前后端
start_all() {
    print_info "准备启动前后端..."
    print_info "将在两个终端窗口中启动服务"
    echo ""

    # 检查依赖
    check_dependencies

    # 启动后端（后台）
    print_info "启动后端..."
    (start_backend) &
    BACKEND_PID=$!

    sleep 3

    # 启动前端（前台）
    print_info "启动前端..."
    start_frontend
}

# 停止所有服务
stop_all() {
    print_info "停止所有服务..."
    pkill -f "uvicorn" || true
    pkill -f "vite" || true
    print_success "所有服务已停止"
}

# 显示日志
show_logs() {
    print_info "显示后端日志..."
    tail -f /tmp/eaios-backend.log
}

# 查看状态
check_status() {
    print_info "检查服务状态..."
    echo ""

    if curl -s http://localhost:8000/api/health > /dev/null; then
        print_success "后端: 运行中 (http://localhost:8000)"
    else
        print_error "后端: 未运行"
    fi

    if curl -s http://localhost:5173 > /dev/null; then
        print_success "前端: 运行中 (http://localhost:5173)"
    else
        print_error "前端: 未运行"
    fi
}

# 主菜单
show_menu() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║       EAIOS 服务管理工具              ║"
    echo "╠════════════════════════════════════════╣"
    echo "║ 1. 启动后端服务                       ║"
    echo "║ 2. 启动前端服务                       ║"
    echo "║ 3. 启动前后端                         ║"
    echo "║ 4. 停止所有服务                       ║"
    echo "║ 5. 检查服务状态                       ║"
    echo "║ 6. 查看帮助                           ║"
    echo "║ 7. 退出                               ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
}

# 显示帮助
show_help() {
    cat << EOF
EAIOS 服务管理工具

用法: ./manage_services.sh [命令]

命令:
  start-backend   启动后端服务 (http://localhost:8000)
  start-frontend  启动前端服务 (http://localhost:5173)
  start-all       启动前后端
  stop            停止所有服务
  status          检查服务状态
  help            显示此帮助信息

环境变量:
  OPENAI_API_KEY  OpenAI API 密钥（必需）

例子:
  # 启动后端
  ./manage_services.sh start-backend

  # 启动前端
  ./manage_services.sh start-frontend

  # 同时启动前后端
  OPENAI_API_KEY=sk-... ./manage_services.sh start-all

EOF
}

# 主逻辑
if [ $# -eq 0 ]; then
    while true; do
        show_menu
        read -p "请选择 (1-7): " choice
        case $choice in
            1) start_backend ;;
            2) start_frontend ;;
            3) start_all ;;
            4) stop_all ;;
            5) check_status ;;
            6) show_help ;;
            7) print_info "退出"; exit 0 ;;
            *) print_error "无效选择" ;;
        esac
    done
else
    case $1 in
        start-backend) start_backend ;;
        start-frontend) start_frontend ;;
        start-all) start_all ;;
        stop) stop_all ;;
        status) check_status ;;
        help) show_help ;;
        *) print_error "未知命令: $1"; show_help; exit 1 ;;
    esac
fi
