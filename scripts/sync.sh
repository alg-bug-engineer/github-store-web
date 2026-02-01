#!/bin/bash
#
# GitHub Releases Store - 数据同步脚本
#
# 使用方法:
#   ./scripts/sync.sh              # 完整同步
#   ./scripts/sync.sh --popular    # 仅同步热门仓库
#   ./scripts/sync.sh --help       # 显示帮助
#

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"

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

# 显示帮助
show_help() {
    cat <<EOF
GitHub Releases Store - 数据同步脚本

使用方法:
    $(basename "$0") [选项]

选项:
    --popular, -p       仅同步预定义的热门仓库（推荐首次使用）
    --full, -f          完整同步（搜索 GitHub 上的热门仓库）
    --limit N           限制每个类别同步的仓库数量（默认: 10）
    --help, -h          显示此帮助信息

示例:
    $(basename "$0") --popular           # 快速同步热门仓库
    $(basename "$0") --full --limit 5    # 完整同步，每类限制 5 个
EOF
}

# 检查环境
check_env() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "未找到 docker-compose.prod.yml 文件"
        print_info "请确保在项目根目录运行此脚本"
        exit 1
    fi

    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "data-service.*Up"; then
        print_error "data-service 容器未运行"
        print_info "请先部署服务: docker-compose -f docker-compose.prod.yml up -d"
        exit 1
    fi
}

# 解析参数
SYNC_MODE=""
LIMIT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --popular|-p)
            SYNC_MODE="--popular-only"
            shift
            ;;
        --full|-f)
            SYNC_MODE=""
            shift
            ;;
        --limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 主逻辑
check_env

echo "=============================================="
print_info "开始数据同步..."
echo "=============================================="
echo ""

# 构建命令
CMD="python scripts/sync_data.py $SYNC_MODE $LIMIT"

print_cmd "$CMD"
echo ""

# 执行同步
docker-compose -f "$COMPOSE_FILE" exec data-service $CMD

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    print_info "✓ 数据同步完成!"
    echo "=============================================="
else
    echo ""
    print_error "✗ 数据同步失败"
    exit 1
fi
