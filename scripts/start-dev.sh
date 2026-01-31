#!/bin/bash

# ============================================
# GitHub Releases Store - 开发环境启动脚本
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo ""
echo "=========================================="
echo "  GitHub Releases Store - 开发环境启动"
echo "=========================================="
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    print_error "Docker 未运行，请先启动 Docker"
    exit 1
fi

# 启动数据库服务
print_info "启动 PostgreSQL 和 Redis..."
docker-compose up -d

# 等待数据库就绪
print_info "等待数据库就绪..."
sleep 5

# 检查后端环境
if [ ! -f "backend/.env" ]; then
    print_warning "未找到 backend/.env，正在从示例文件复制..."
    cp backend/.env.example backend/.env
    print_warning "请编辑 backend/.env 配置必要的环境变量"
fi

# 检查前端环境
if [ ! -f "frontend/.env.local" ]; then
    print_warning "未找到 frontend/.env.local，正在创建..."
    echo 'VITE_API_BASE_URL=http://localhost:8000/api/v1' > frontend/.env.local
fi

# 检查 Python 虚拟环境
if [ ! -d "backend/venv" ]; then
    print_info "创建 Python 虚拟环境..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    source backend/venv/bin/activate
fi

# 检查 Node 依赖
if [ ! -d "frontend/node_modules" ]; then
    print_info "安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 运行数据库迁移
print_info "运行数据库迁移..."
cd backend
alembic upgrade head 2>/dev/null || print_warning "迁移失败或已是最新"
cd ..

print_success "环境准备完成！"
echo ""
echo "=========================================="
echo "  启动服务"
echo "=========================================="
echo ""
echo "请在不同的终端窗口中运行以下命令："
echo ""
echo "1. 启动后端 (终端 1):"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. 启动前端 (终端 2):"
echo "   cd frontend && npm run dev"
echo ""
echo "3. 同步数据 (可选):"
echo "   cd backend && source venv/bin/activate && python scripts/sync_data.py"
echo ""
echo "=========================================="
echo "  访问地址"
echo "=========================================="
echo ""
echo "  前端:     http://localhost:5173"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo ""
