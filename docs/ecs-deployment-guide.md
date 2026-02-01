# GitHub Releases Store - 阿里云 ECS 完整部署指南

本文档详细介绍如何将 GitHub Releases Store 项目完整部署到阿里云 ECS 服务器，包括数据服务、后端 API、前端应用以及 Nginx 反向代理的全套部署流程。

## 目录

1. [架构概览](#架构概览)
2. [准备工作](#准备工作)
3. [ECS 服务器配置](#ecs-服务器配置)
4. [项目部署](#项目部署)
5. [域名与 HTTPS 配置](#域名与-https-配置)
6. [监控与维护](#监控与维护)
7. [故障排查](#故障排查)
8. [备份与恢复](#备份与恢复)

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              用户浏览器                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Nginx (反向代理 + HTTPS)                         │
│                         端口: 80 / 443                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│    前端 (Vue 3)      │ │   后端 (FastAPI)     │ │  数据服务 (FastAPI)  │
│    - 静态文件        │ │   - REST API        │ │  - Health API       │
│    - 端口: 80       │ │   - 端口: 8000      │ │  - 端口: 8001       │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
                                                      │
                                ┌─────────────────────┼─────────────────────┐
                                ▼                     ▼                     ▼
                       ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
                       │  Celery Worker  │ │  Celery Beat    │ │  PostgreSQL     │
                       │  (后台任务)      │ │  (定时调度)      │ │  数据库          │
                       └─────────────────┘ └─────────────────┘ └─────────────────┘
                                                                              │
                                                                ┌─────────────┘
                                                                ▼
                                                       ┌─────────────────┐
                                                       │     Redis       │
                                                       │  缓存/消息队列   │
                                                       └─────────────────┘
```

### 服务说明

| 服务 | 说明 | 容器名称 | 端口 |
|------|------|----------|------|
| nginx | 反向代理，处理所有外部请求 | nginx | 80, 443 |
| frontend | Vue 3 前端应用 | frontend | 80 (内部) |
| backend | FastAPI 后端 API | backend | 8000 (内部) |
| data-service | 数据服务 Health API | data-service | 8001 (内部) |
| data-celery-worker | Celery 后台任务处理器 | data-celery-worker | - |
| data-celery-beat | Celery 定时任务调度器 | data-celery-beat | - |
| db | PostgreSQL 数据库 | db | - (内部) |
| redis | Redis 缓存和消息队列 | redis | - (内部) |

---

## 准备工作

### 1. 购买和配置 ECS 服务器

**推荐配置:**
- **实例规格**: 2核 4GB 或更高（生产环境建议 4核 8GB）
- **操作系统**: Ubuntu 22.04 LTS (64位)
- **系统盘**: 40GB SSD 或更高
- **数据盘**: 建议单独挂载数据盘用于数据存储
- **公网带宽**: 5Mbps 或更高
- **安全组规则**:

| 端口 | 协议 | 授权对象 | 说明 |
|------|------|----------|------|
| 22 | TCP | 你的 IP | SSH 访问 |
| 80 | TCP | 0.0.0.0/0 | HTTP 访问 |
| 443 | TCP | 0.0.0.0/0 | HTTPS 访问 |

### 2. 准备域名（可选但推荐）

- 在阿里云或其他域名服务商购买域名
- 添加 A 记录指向 ECS 公网 IP

### 3. 准备 API 密钥

- **GitHub Token**: 访问 https://github.com/settings/tokens 生成 Personal Access Token，勾选 `public_repo` 权限
- **Kimi API Key**（可选）: 访问 https://platform.moonshot.cn/ 获取 API 密钥

---

## ECS 服务器配置

### 1. 连接服务器

```bash
ssh root@your-ecs-ip
```

### 2. 系统更新

```bash
apt update && apt upgrade -y
```

### 3. 安装 Docker

```bash
# 安装必要依赖
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 软件源
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

### 4. 配置 Docker 镜像加速（阿里云）

```bash
# 登录阿里云容器镜像服务获取加速器地址：https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
# 创建配置文件
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": ["https://your-mirror-id.mirror.aliyuncs.com"]
}
EOF

# 重启 Docker
systemctl daemon-reload
systemctl restart docker
```

### 5. 创建部署用户（可选但推荐）

```bash
# 创建用户
useradd -m -s /bin/bash deploy
usermod -aG docker deploy

# 设置密码
passwd deploy

# 切换到 deploy 用户
su - deploy
```

---

## 项目部署

### 1. 克隆项目代码

```bash
cd ~
git clone https://github.com/your-username/github-store-web.git
cd github-store-web
```

### 2. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env.production

# 编辑配置文件
vim .env.production
```

**完整的环境变量配置示例:**

```ini
# ============================================
# 数据库配置（必须）
# ============================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YourStrongPassword123!  # 生产环境使用强密码
POSTGRES_DB=github_store

# ============================================
# 安全配置（必须）
# ============================================
# JWT 密钥，使用以下命令生成：
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secret-key-here

# ============================================
# GitHub API 配置（必须）
# ============================================
GITHUB_TOKEN=ghp_your_github_personal_access_token

# ============================================
# Kimi AI 配置（可选）
# ============================================
KIMI_API_KEY=sk-your-kimi-api-key
KIMI_API_BASE=https://api.moonshot.cn

# ============================================
# CORS 配置
# ============================================
# 如果你有域名，替换 localhost 为你的域名
BACKEND_CORS_ORIGINS=["http://localhost","http://your-domain.com","https://your-domain.com"]

# ============================================
# 前端配置
# ============================================
VITE_API_BASE_URL=/api/v1

# ============================================
# 端口配置
# ============================================
HTTP_PORT=80
HTTPS_PORT=443
```

### 3. 创建 SSL 证书目录

```bash
mkdir -p nginx/ssl
```

如果使用 HTTP 部署，可以跳过此步骤。如需 HTTPS，请参考下方的 [域名与 HTTPS 配置](#域名与-https-配置)。

### 4. 首次部署（完整流程）

```bash
# 1. 构建并启动所有服务（后台运行）
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 2. 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 3. 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. 数据库初始化

等待所有服务启动后，执行数据库迁移：

```bash
# 执行数据库迁移
docker-compose -f docker-compose.prod.yml exec data-service alembic upgrade head

# 检查迁移状态
docker-compose -f docker-compose.prod.yml exec data-service alembic current
```

### 6. 初始数据同步

```bash
# 执行初始数据同步（同步热门仓库）
docker-compose -f docker-compose.prod.yml exec data-service python scripts/sync_data.py --popular-only

# 或者完整同步（耗时较长）
# docker-compose -f docker-compose.prod.yml exec data-service python scripts/sync_data.py
```

### 7. 验证部署

```bash
# 检查所有容器状态
docker-compose -f docker-compose.prod.yml ps

# 检查 Nginx 是否正常运行
curl http://localhost/health

# 检查后端 API
curl http://localhost/api/v1/health

# 检查数据服务
curl http://localhost:8001/health  # 内部访问
```

浏览器访问：`http://your-ecs-ip`

---

## 域名与 HTTPS 配置

### 方案一：使用 Certbot + Let's Encrypt（推荐）

#### 1. 修改 Nginx 配置支持 HTTPS

编辑 `nginx/nginx.conf`，取消 HTTPS server 部分的注释并修改域名：

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    client_max_body_size 50M;

    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    upstream frontend {
        server frontend:80;
        keepalive 32;
    }

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;

        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";

            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;

            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        location ~ ^/(docs|redoc|openapi.json) {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
        }

        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

#### 2. 使用 Certbot 申请证书

```bash
# 安装 Certbot
apt install -y certbot

# 停止 Nginx 容器（释放 80 端口）
docker-compose -f docker-compose.prod.yml stop nginx

# 申请证书（替换 your-domain.com 为你的域名）
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# 复制证书到项目目录
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/

# 重新启动 Nginx
docker-compose -f docker-compose.prod.yml up -d nginx
```

#### 3. 设置自动续期

```bash
# 创建续期脚本
cat > /opt/renew-ssl.sh <<'EOF'
#!/bin/bash

# 续期证书
certbot renew --quiet

# 复制新证书
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /path/to/github-store-web/nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /path/to/github-store-web/nginx/ssl/

# 重启 Nginx 容器
cd /path/to/github-store-web
docker-compose -f docker-compose.prod.yml restart nginx
EOF

chmod +x /opt/renew-ssl.sh

# 添加到 crontab，每月执行一次
echo "0 0 1 * * /opt/renew-ssl.sh" | crontab -
```

### 方案二：使用阿里云 SSL 证书

1. 登录阿里云 SSL 证书控制台
2. 购买/申请免费证书
3. 下载 Nginx 格式的证书
4. 上传到服务器的 `nginx/ssl/` 目录
5. 修改 `nginx/nginx.conf` 中的证书路径
6. 重启 Nginx 容器

---

## 监控与维护

### 日常维护命令

```bash
# 查看所有服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看实时日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f data-celery-worker

# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启单个服务
docker-compose -f docker-compose.prod.yml restart backend

# 更新代码后重新部署
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# 执行数据库迁移
docker-compose -f docker-compose.prod.yml exec data-service alembic upgrade head

# 手动触发数据同步
docker-compose -f docker-compose.prod.yml exec data-service python scripts/sync_data.py
```

### 监控资源使用

```bash
# 查看容器资源使用
docker stats

# 查看磁盘空间
df -h

# 查看内存使用
free -h

# 查看数据库大小
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('github_store'));"
```

### 查看 Celery 任务状态

```bash
# 查看 Worker 日志
docker-compose -f docker-compose.prod.yml logs -f data-celery-worker

# 查看 Beat 调度日志
docker-compose -f docker-compose.prod.yml logs -f data-celery-beat
```

---

## 故障排查

### 1. 容器无法启动

```bash
# 查看具体错误
docker-compose -f docker-compose.prod.yml logs [service-name]

# 常见原因：
# - 端口被占用：netstat -tlnp | grep 80
# - 环境变量错误：检查 .env.production
# - 镜像构建失败：docker-compose -f docker-compose.prod.yml build --no-cache
```

### 2. 数据库连接失败

```bash
# 检查数据库容器
docker-compose -f docker-compose.prod.yml ps db
docker-compose -f docker-compose.prod.yml logs db

# 手动连接数据库测试
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d github_store

# 检查后端数据库连接配置
docker-compose -f docker-compose.prod.yml exec backend env | grep POSTGRES
```

### 3. 前端无法访问 API

```bash
# 检查后端服务
docker-compose -f docker-compose.prod.yml ps backend
docker-compose -f docker-compose.prod.yml logs backend

# 测试内部网络连通性
docker-compose -f docker-compose.prod.yml exec nginx ping backend

# 检查 CORS 配置
docker-compose -f docker-compose.prod.yml exec backend env | grep CORS
```

### 4. 数据同步失败

```bash
# 检查 GitHub Token 是否有效
docker-compose -f docker-compose.prod.yml exec data-service env | grep GITHUB_TOKEN

# 手动运行同步脚本查看错误
docker-compose -f docker-compose.prod.yml exec data-service python scripts/sync_data.py

# 检查 Worker 是否运行
docker-compose -f docker-compose.prod.yml ps data-celery-worker
```

### 5. Nginx 502 错误

```bash
# 检查后端服务是否健康
docker-compose -f docker-compose.prod.yml ps

# 查看 Nginx 错误日志
docker-compose -f docker-compose.prod.yml logs nginx

# 检查上游服务
docker-compose -f docker-compose.prod.yml exec nginx wget -qO- http://backend:8000/api/v1/health
```

### 6. 内存不足

```bash
# 添加 Swap 空间
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 或者升级 ECS 实例配置
```

---

## 备份与恢复

### 数据库备份

```bash
# 创建备份脚本
cat > /opt/backup-db.sh <<'EOF'
#!/bin/bash

BACKUP_DIR="/backups/github-store"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose -f /path/to/github-store-web/docker-compose.prod.yml exec -T db pg_dump -U postgres github_store | gzip > $BACKUP_DIR/github_store_$DATE.sql.gz

# 保留最近 7 天的备份
find $BACKUP_DIR -name "github_store_*.sql.gz" -mtime +7 -delete

# 可选：上传到阿里云 OSS
# aliyun oss cp $BACKUP_DIR/github_store_$DATE.sql.gz oss://your-bucket/backups/
EOF

chmod +x /opt/backup-db.sh

# 设置每天凌晨 2 点自动备份
echo "0 2 * * * /opt/backup-db.sh" | crontab -
```

### 数据库恢复

```bash
# 停止相关服务
docker-compose -f docker-compose.prod.yml stop backend data-service

# 恢复数据库
gunzip < /backups/github_store_20240101_020000.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres -d github_store

# 启动服务
docker-compose -f docker-compose.prod.yml start backend data-service
```

### 数据卷备份

```bash
# 备份 Docker 卷
docker run --rm -v github-store-web_postgres_data:/data -v /backups:/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz -C /data .

# 恢复 Docker 卷
docker run --rm -v github-store-web_postgres_data:/data -v /backups:/backup alpine sh -c "cd /data && tar xzf /backup/postgres_data_20240101.tar.gz"
```

---

## 更新部署

### 平滑更新流程

```bash
cd ~/github-store-web

# 1. 拉取最新代码
git pull

# 2. 备份当前运行状态
docker-compose -f docker-compose.prod.yml ps > /tmp/pre-deploy-status.txt

# 3. 执行数据库迁移（先启动数据库）
docker-compose -f docker-compose.prod.yml up -d db redis
docker-compose -f docker-compose.prod.yml exec data-service alembic upgrade head

# 4. 重新构建并启动其他服务
docker-compose -f docker-compose.prod.yml up -d --build backend frontend data-service data-celery-worker data-celery-beat nginx

# 5. 验证服务状态
docker-compose -f docker-compose.prod.yml ps
curl -f http://localhost/health || echo "Health check failed!"

# 6. 如有问题，回滚到上一版本
git log --oneline -5  # 查看历史提交
git reset --hard HEAD~1  # 回滚到上一版本
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 安全建议

1. **定期更新系统**
   ```bash
   apt update && apt upgrade -y
   ```

2. **配置防火墙**
   ```bash
   ufw default deny incoming
   ufw default allow outgoing
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

3. **禁用 root SSH 登录**
   ```bash
   vim /etc/ssh/sshd_config
   # 设置 PermitRootLogin no
   # 设置 PasswordAuthentication no（如果使用密钥登录）
   systemctl restart sshd
   ```

4. **定期更换密钥和密码**
   - GitHub Token 定期更换
   - 数据库密码定期更换
   - JWT Secret 定期更换

5. **启用阿里云安全服务**
   - 云防火墙
   - 安骑士（主机安全）
   - Web 应用防火墙（WAF）

---

## 联系支持

如遇到问题，请查看：

1. 服务日志：`docker-compose -f docker-compose.prod.yml logs`
2. 系统日志：`journalctl -xe`
3. 项目文档：`docs/` 目录

---

**部署完成！** 你的 GitHub Releases Store 应用现在应该可以通过 `http://your-ecs-ip` 或 `https://your-domain.com` 访问了。
