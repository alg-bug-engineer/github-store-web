#!/bin/bash

# ============================================
# GitHub Releases Store - 生产环境部署脚本
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
echo "  GitHub Releases Store - 生产环境部署"
echo "=========================================="
echo ""

# 检查环境变量文件
if [ ! -f ".env.production" ]; then
    print_error "未找到 .env.production 文件"
    print_info "请复制 .env.example 并配置生产环境变量:"
    echo "  cp .env.example .env.production"
    echo "  vim .env.production"
    exit 1
fi

# 检查必要的环境变量
source .env.production

if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "your_secure_password_here" ]; then
    print_error "请在 .env.production 中设置安全的 POSTGRES_PASSWORD"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "change-this-to-a-random-secret-key" ]; then
    print_error "请在 .env.production 中设置安全的 SECRET_KEY"
    print_info "生成方法: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    exit 1
fi

if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ]; then
    print_warning "GITHUB_TOKEN 未配置，将无法同步 GitHub 数据"
fi

# 创建必要的目录
print_info "创建必要的目录..."
mkdir -p nginx/ssl

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    print_error "Docker 未运行，请先启动 Docker"
    exit 1
fi

# 停止旧服务
print_info "停止旧服务..."
docker-compose -f docker-compose.prod.yml --env-file .env.production down 2>/dev/null || true

# 构建并启动服务
print_info "构建并启动服务..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 等待服务就绪
print_info "等待服务就绪..."
sleep 10

# 运行数据库迁移
print_info "运行数据库迁移..."
docker-compose -f docker-compose.prod.yml --env-file .env.production exec -T backend alembic upgrade head

# 检查服务状态
print_info "检查服务状态..."
docker-compose -f docker-compose.prod.yml --env-file .env.production ps

echo ""
print_success "部署完成！"
echo ""
echo "=========================================="
echo "  访问地址"
echo "=========================================="
echo ""
echo "  网站:     http://localhost"
echo "  API 文档: http://localhost/docs"
echo ""
echo "=========================================="
echo "  常用命令"
echo "=========================================="
echo ""
echo "查看日志:"
echo "  docker-compose -f docker-compose.prod.yml --env-file .env.production logs -f"
echo ""
echo "同步数据:"
echo "  docker-compose -f docker-compose.prod.yml --env-file .env.production exec backend python scripts/sync_data.py"
echo ""
echo "停止服务:"
echo "  docker-compose -f docker-compose.prod.yml --env-file .env.production down"
echo ""
