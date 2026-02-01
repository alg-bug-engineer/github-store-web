#!/bin/bash
#
# GitHub Releases Store - 生产环境部署脚本
#
# 使用方法:
#   ./deploy_prod.sh          # 标准部署（保留数据）
#   ./deploy_prod.sh --fresh  # 全新部署（清空数据）
#   ./deploy_prod.sh --skip-build  # 跳过构建，仅重启
#

set -e

# 配置
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
FRESH_DEPLOY=false
SKIP_BUILD=false

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_cmd() {
    echo -e "${BLUE}[CMD]${NC} $1"
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --fresh)
            FRESH_DEPLOY=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --help|-h)
            echo "GitHub Releases Store - 生产环境部署脚本"
            echo ""
            echo "使用方法:"
            echo "    $(basename "$0") [选项]"
            echo ""
            echo "选项:"
            echo "    --fresh         全新部署（清空所有数据）"
            echo "    --skip-build    跳过构建，仅重启服务"
            echo "    --help, -h      显示此帮助"
            echo ""
            echo "示例:"
            echo "    $(basename "$0")              # 标准部署"
            echo "    $(basename "$0") --fresh      # 全新部署"
            echo "    $(basename "$0") --skip-build # 快速重启"
            exit 0
            ;;
        *)
            print_error "未知选项: $1"
            exit 1
            ;;
    esac
done

# 检查环境文件
if [ ! -f "$ENV_FILE" ]; then
    print_error "未找到生产环境配置文件: $ENV_FILE"
    print_info "请复制 .env.example 创建配置文件:"
    print_info "  cp .env.example $ENV_FILE"
    print_info "  vim $ENV_FILE  # 编辑配置"
    exit 1
fi

print_info "使用配置文件: $ENV_FILE"

# 检查 Docker
docker --version > /dev/null 2>&1 || {
    print_error "Docker 未安装"
    exit 1
}

# 停止服务
if [ "$FRESH_DEPLOY" = true ]; then
    echo ""
    print_warn "⚠️  警告: 这将删除所有数据卷！"
    read -p "确定要继续吗? (yes/no) " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_info "操作已取消"
        exit 0
    fi
    echo ""
    print_info "停止并删除所有服务和数据卷..."
    docker-compose -f "$COMPOSE_FILE" down -v
    print_info "服务和数据已清空"
else
    print_info "停止服务（保留数据）..."
    docker-compose -f "$COMPOSE_FILE" down
    print_info "服务已停止"
fi

# 构建并启动
if [ "$SKIP_BUILD" = false ]; then
    print_info "构建并启动服务..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build
else
    print_info "跳过构建，直接启动服务..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
fi

# 等待数据库就绪
print_info "等待数据库就绪..."
sleep 5

RETRIES=0
MAX_RETRIES=30
while ! docker-compose -f "$COMPOSE_FILE" exec -T db pg_isready -U postgres > /dev/null 2>&1; do
    RETRIES=$((RETRIES + 1))
    if [ $RETRIES -ge $MAX_RETRIES ]; then
        print_error "数据库启动超时"
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""
print_info "数据库已就绪"

# 执行数据库迁移
print_info "执行数据库迁移..."
docker-compose -f "$COMPOSE_FILE" exec -T data-service alembic upgrade head
print_info "数据库迁移完成"

# 全新部署：执行初始数据同步
if [ "$FRESH_DEPLOY" = true ]; then
    echo ""
    print_info "开始初始数据同步..."
    print_info "这将同步 GitHub 热门仓库数据，可能需要几分钟..."
    docker-compose -f "$COMPOSE_FILE" exec data-service python scripts/sync_data.py --popular-only
    print_info "初始数据同步完成"
fi

# 健康检查
echo ""
print_info "执行健康检查..."
sleep 3

if curl -sf http://localhost/health > /dev/null 2>&1; then
    print_info "✓ Nginx 健康检查通过"
else
    print_warn "✗ Nginx 健康检查未通过，服务可能仍在启动中"
fi

# 显示状态
echo ""
print_info "服务状态:"
docker-compose -f "$COMPOSE_FILE" ps

echo ""
echo "=============================================="
print_info "🎉 部署成功!"
echo "=============================================="
echo ""
echo "访问地址:"
echo "  - HTTP:  http://localhost"
echo ""
echo "常用命令:"
echo "  查看日志:   docker-compose -f $COMPOSE_FILE logs -f"
echo "  重启服务:   docker-compose -f $COMPOSE_FILE restart"
echo "  数据同步:   docker-compose -f $COMPOSE_FILE exec data-service python scripts/sync_data.py"
echo "  查看状态:   docker-compose -f $COMPOSE_FILE ps"
echo ""
