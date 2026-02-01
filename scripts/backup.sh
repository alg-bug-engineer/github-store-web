#!/bin/bash
#
# GitHub Releases Store - 数据库备份脚本
#
# 使用方法:
#   ./scripts/backup.sh                    # 备份到默认目录
#   ./scripts/backup.sh /path/to/backup    # 备份到指定目录
#

set -e

# 配置
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${1:-/backups/github-store}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查 Docker Compose 文件
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
    print_error "未找到 docker-compose.prod.yml 文件"
    exit 1
fi

# 检查数据库容器是否运行
if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "db.*Up"; then
    print_error "数据库容器未运行"
    exit 1
fi

print_info "开始备份数据库..."

# 执行备份
BACKUP_FILE="$BACKUP_DIR/github_store_$DATE.sql.gz"
if docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres github_store | gzip > "$BACKUP_FILE"; then
    print_info "✓ 备份成功: $BACKUP_FILE"
    
    # 显示备份大小
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    print_info "备份大小: $SIZE"
else
    print_error "备份失败"
    exit 1
fi

# 清理旧备份
print_info "清理 $RETENTION_DAYS 天前的旧备份..."
DELETED=$(find "$BACKUP_DIR" -name "github_store_*.sql.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
print_info "已删除 $DELETED 个旧备份文件"

# 显示备份列表
print_info "当前备份文件列表:"
ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null | tail -5

echo ""
print_info "备份完成!"
