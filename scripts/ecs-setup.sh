#!/bin/bash
#
# GitHub Releases Store - ECS 一键部署脚本
#
# 使用方法:
#   chmod +x scripts/ecs-setup.sh
#   ./scripts/ecs-setup.sh
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    print_error "请使用 root 用户运行此脚本"
    exit 1
fi

# 检查系统
if [ ! -f /etc/os-release ]; then
    print_error "无法识别操作系统"
    exit 1
fi

source /etc/os-release
if [[ "$ID" != "ubuntu" ]]; then
    print_warn "此脚本针对 Ubuntu 优化，当前系统: $ID"
    read -p "是否继续? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

print_info "开始部署 GitHub Releases Store..."

# 1. 系统更新
print_info "正在更新系统..."
apt update && apt upgrade -y

# 2. 安装基础依赖
print_info "正在安装基础依赖..."
apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    vim \
    ufw

# 3. 安装 Docker
if ! command -v docker &> /dev/null; then
    print_info "正在安装 Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    print_info "Docker 安装完成"
else
    print_info "Docker 已安装，跳过..."
fi

# 验证 Docker
docker --version
docker compose version

# 4. 配置防火墙
print_info "正在配置防火墙..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
print_info "防火墙配置完成"

# 5. 创建项目目录
PROJECT_DIR="/opt/github-store-web"
print_info "项目将部署到: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    print_warn "目录已存在: $PROJECT_DIR"
    read -p "是否删除并重新克隆? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
    else
        print_info "使用现有目录..."
    fi
fi

if [ ! -d "$PROJECT_DIR" ]; then
    print_info "请输入 Git 仓库地址:"
    read -r GIT_REPO
    git clone "$GIT_REPO" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# 6. 配置环境变量
if [ ! -f ".env.production" ]; then
    print_info "创建环境变量配置文件..."
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -base64 32)
    
    cat > .env.production <<EOF
# ============================================
# 数据库配置
# ============================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 20)
POSTGRES_DB=github_store

# ============================================
# 安全配置
# ============================================
SECRET_KEY=$SECRET_KEY

# ============================================
# GitHub API 配置（请修改）
# ============================================
GITHUB_TOKEN=your_github_token_here

# ============================================
# Kimi AI 配置（可选）
# ============================================
KIMI_API_KEY=
KIMI_API_BASE=https://api.moonshot.cn

# ============================================
# CORS 配置
# ============================================
BACKEND_CORS_ORIGINS=["http://localhost"]

# ============================================
# 前端配置
# ============================================
VITE_API_BASE_URL=/api/v1

# ============================================
# 端口配置
# ============================================
HTTP_PORT=80
HTTPS_PORT=443
EOF

    print_warn "请编辑 .env.production 文件，配置你的 GitHub Token 和其他参数"
    print_info "文件路径: $PROJECT_DIR/.env.production"
    
    # 显示生成的配置
    echo ""
    echo "=============================================="
    cat .env.production
    echo "=============================================="
    echo ""
    
    read -p "编辑完成后按回车继续..."
fi

# 7. 创建 SSL 目录
mkdir -p nginx/ssl

# 8. 部署服务
print_info "正在部署服务..."
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 9. 等待服务启动
print_info "等待服务启动..."
sleep 15

# 10. 执行数据库迁移
print_info "执行数据库迁移..."
docker-compose -f docker-compose.prod.yml exec -T data-service alembic upgrade head || {
    print_warn "数据库迁移可能需要等待数据库完全启动，5秒后重试..."
    sleep 5
    docker-compose -f docker-compose.prod.yml exec -T data-service alembic upgrade head
}

# 11. 检查服务状态
print_info "检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 12. 健康检查
print_info "执行健康检查..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_info "✓ Nginx 健康检查通过"
else
    print_error "✗ Nginx 健康检查失败"
fi

# 13. 显示部署信息
IP_ADDRESS=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "your-ecs-ip")

echo ""
echo "=============================================="
echo "🎉 部署完成!"
echo "=============================================="
echo ""
echo "访问地址:"
echo "  - HTTP:  http://$IP_ADDRESS"
echo ""
echo "常用命令:"
echo "  查看状态:   docker-compose -f docker-compose.prod.yml ps"
echo "  查看日志:   docker-compose -f docker-compose.prod.yml logs -f"
echo "  重启服务:   docker-compose -f docker-compose.prod.yml restart"
echo "  数据同步:   docker-compose -f docker-compose.prod.yml exec data-service python scripts/sync_data.py"
echo ""
echo "项目目录: $PROJECT_DIR"
echo "配置文件: $PROJECT_DIR/.env.production"
echo ""
echo "下一步:"
echo "  1. 配置域名解析到服务器 IP: $IP_ADDRESS"
echo "  2. 配置 HTTPS SSL 证书（参考 docs/ecs-deployment-guide.md）"
echo "  3. 执行初始数据同步"
echo ""
echo "=============================================="
