# GitHub Releases Store 部署指南

本文档提供完整的项目部署教程，包括开发环境和生产环境的配置说明。

## 目录

1. [项目架构](#项目架构)
2. [环境要求](#环境要求)
3. [快速开始（开发环境）](#快速开始开发环境)
4. [环境变量配置](#环境变量配置)
5. [Docker 部署（生产环境）](#docker-部署生产环境)
6. [手动部署](#手动部署)
7. [数据同步](#数据同步)
8. [常见问题](#常见问题)

---

## 项目架构

```
┌─────────────────────────────────────────────────────────────┐
│                         客户端浏览器                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (反向代理)                          │
│                    - 前端静态文件                             │
│                    - API 代理到后端                           │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│     前端 (Vue 3)         │     │    后端 (FastAPI)        │
│     - Vite 构建          │     │    - REST API           │
│     - Tailwind CSS      │     │    - 用户认证             │
│     - 端口: 80/443      │     │    - 端口: 8000          │
└─────────────────────────┘     └─────────────────────────┘
                                              │
              ┌───────────────┬───────────────┼───────────────┐
              ▼               ▼               ▼               ▼
┌───────────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   PostgreSQL      │ │    Redis      │ │   Celery      │ │  外部 API     │
│   数据库          │ │   缓存/消息队列│ │   后台任务    │ │  GitHub/Kimi │
│   端口: 5432      │ │   端口: 6379  │ │               │ │               │
└───────────────────┘ └───────────────┘ └───────────────┘ └───────────────┘
```

---

## 环境要求

### 软件版本

| 软件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Node.js | 20.19.0 | 22.x |
| Python | 3.10 | 3.11+ |
| PostgreSQL | 14 | 15 |
| Redis | 6 | 7 |
| Docker | 20.10 | 24.x |
| Docker Compose | 2.0 | 2.20+ |

### 系统要求

- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 10GB 可用空间
- **操作系统**: Linux (Ubuntu 20.04+), macOS, Windows (WSL2)

---

## 快速开始（开发环境）

### 1. 克隆项目

```bash
git clone <repository-url>
cd github-store-web
```

### 2. 启动数据库服务

```bash
# 使用 Docker Compose 启动 PostgreSQL 和 Redis
docker-compose up -d
```

### 3. 配置后端

```bash
cd backend

# 创建 Python 虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置文件
cp .env.example .env

# 编辑 .env 文件，配置必要的变量（见下文）
```

### 4. 初始化数据库

```bash
# 在 backend 目录下
# 运行数据库迁移
alembic upgrade head

# 运行数据回填脚本，初始化新增字段数据
python scripts/backfill_repo_metadata.py
```

### 5. 启动后端服务

```bash
# 开发模式启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 配置并启动前端

```bash
cd frontend

# 安装依赖
npm install

# 创建环境变量文件
echo 'VITE_API_BASE_URL=http://localhost:8000/api/v1' > .env.local

# 启动开发服务器
npm run dev
```

### 7. 同步 GitHub 数据

```bash
cd backend

# 运行数据同步脚本
python scripts/sync_data.py
```

### 8. 访问应用

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 环境变量配置

### 后端环境变量 (`backend/.env`)

```bash
# ============================================
# 数据库配置
# ============================================
# PostgreSQL 服务器地址
POSTGRES_SERVER=localhost

# PostgreSQL 用户名
POSTGRES_USER=postgres

# PostgreSQL 密码（生产环境请使用强密码）
POSTGRES_PASSWORD=your_secure_password

# 数据库名称
POSTGRES_DB=github_store

# 完整的数据库连接 URL（可选，会自动生成）
# DATABASE_URL=postgresql://postgres:password@localhost/github_store

# ============================================
# Redis 配置
# ============================================
# Redis 服务器地址
REDIS_HOST=localhost

# Redis 端口
REDIS_PORT=6379

# ============================================
# Celery 配置（后台任务）
# ============================================
# Celery 消息代理 URL
CELERY_BROKER_URL=redis://localhost:6379/0

# Celery 结果后端 URL
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ============================================
# 安全配置
# ============================================
# JWT 密钥（生产环境必须更改！）
# 生成方法: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-super-secret-key-change-in-production

# Token 过期时间（分钟），默认 7 天
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# ============================================
# GitHub API 配置
# ============================================
# GitHub Personal Access Token
# 获取方法: GitHub -> Settings -> Developer settings -> Personal access tokens
# 需要的权限: public_repo (读取公开仓库)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# Kimi AI 配置（可选）
# ============================================
# Kimi API 密钥
# 获取方法: https://platform.moonshot.cn/
KIMI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Kimi API 基础 URL
KIMI_API_BASE=https://api.moonshot.cn

# ============================================
# CORS 配置
# ============================================
# 允许的前端域名列表（JSON 数组格式）
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://your-domain.com"]
```

### 前端环境变量 (`frontend/.env.local`)

```bash
# ============================================
# API 配置
# ============================================
# 后端 API 基础 URL
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 生产环境示例:
# VITE_API_BASE_URL=https://api.your-domain.com/api/v1
```

### 获取 API 密钥

#### GitHub Token

1. 登录 GitHub
2. 进入 Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
3. 点击 "Generate new token (classic)"
4. 勾选 `public_repo` 权限
5. 生成并复制 Token

#### Kimi API Key（可选）

1. 访问 https://platform.moonshot.cn/
2. 注册/登录账号
3. 进入控制台 -> API 密钥
4. 创建新的 API 密钥

---

## Docker 部署（生产环境）

### 1. 准备配置文件

创建生产环境配置文件 `.env.production`：

```bash
# 在项目根目录创建
cp backend/.env.example .env.production

# 编辑配置
vim .env.production
```

### 2. 使用完整的 docker-compose

项目根目录下创建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB:-github_store}
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Redis 缓存
  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # 后端 API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      - POSTGRES_SERVER=db
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB:-github_store}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - KIMI_API_KEY=${KIMI_API_KEY}
      - KIMI_API_BASE=${KIMI_API_BASE:-https://api.moonshot.cn}
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network

  # Celery Worker
  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - POSTGRES_SERVER=db
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB:-github_store}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - KIMI_API_KEY=${KIMI_API_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network

  # 前端
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_BASE_URL=${VITE_API_BASE_URL:-/api/v1}
    restart: always
    networks:
      - app-network

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### 3. 创建 Dockerfile

后端 Dockerfile (`backend/Dockerfile`)：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

前端 Dockerfile (`frontend/Dockerfile`)：

```dockerfile
# 构建阶段
FROM node:22-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 设置构建时环境变量
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# 构建
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

前端 Nginx 配置 (`frontend/nginx.conf`)：

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4. 创建 Nginx 反向代理配置

创建 `nginx/nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # 上游服务
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name localhost;

        # API 代理
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket 支持
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # API 文档
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /redoc {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 前端
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### 5. 部署步骤

```bash
# 1. 创建必要的目录
mkdir -p nginx/ssl

# 2. 配置环境变量
cp backend/.env.example .env.production
# 编辑 .env.production 填入正确的值

# 3. 构建并启动服务
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 4. 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 5. 运行数据库迁移
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 运行数据回填脚本，初始化新增字段数据
docker-compose -f docker-compose.prod.yml exec backend python scripts/backfill_repo_metadata.py

# 6. 同步 GitHub 数据
docker-compose -f docker-compose.prod.yml exec backend python scripts/sync_data.py
```

---

## 手动部署

如果不使用 Docker，可以按以下步骤手动部署。

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server \
    nginx nodejs npm

# 启动服务
sudo systemctl start postgresql redis-server
sudo systemctl enable postgresql redis-server
```

### 2. 配置数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE USER github_store WITH PASSWORD 'your_password';
CREATE DATABASE github_store OWNER github_store;
GRANT ALL PRIVILEGES ON DATABASE github_store TO github_store;
\q
```

### 3. 部署后端

```bash
cd backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn

# 配置环境变量
cp .env.example .env
# 编辑 .env

# 运行迁移
alembic upgrade head

# 使用 Gunicorn 启动
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 4. 配置 Systemd 服务

创建 `/etc/systemd/system/github-store-api.service`：

```ini
[Unit]
Description=GitHub Releases Store API
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/github-store/backend
Environment="PATH=/var/www/github-store/backend/venv/bin"
EnvironmentFile=/var/www/github-store/backend/.env
ExecStart=/var/www/github-store/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start github-store-api
sudo systemctl enable github-store-api
```

### 5. 部署前端

```bash
cd frontend

# 安装依赖
npm ci

# 创建生产环境变量
echo 'VITE_API_BASE_URL=/api/v1' > .env.production

# 构建
npm run build

# 复制到 nginx 目录
sudo cp -r dist/* /var/www/github-store/frontend/
```

### 6. 配置 Nginx

创建 `/etc/nginx/sites-available/github-store`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /var/www/github-store/frontend;
    index index.html;

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API 文档
    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/github-store /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 数据同步

### 手动同步

```bash
# 开发环境
cd backend
python scripts/sync_data.py

# Docker 环境
docker-compose exec backend python scripts/sync_data.py
```

### 数据回填（新字段初始化）

首次部署或新增仓库模型字段后，需要运行此脚本回填数据。

```bash
# 开发环境
cd backend
python scripts/backfill_repo_metadata.py

# Docker 环境
docker-compose exec backend python scripts/backfill_repo_metadata.py
```

### 定时同步（Cron）

```bash
# 编辑 crontab
crontab -e

# 添加每小时同步任务
0 * * * * cd /var/www/github-store/backend && /var/www/github-store/backend/venv/bin/python scripts/sync_data.py >> /var/log/github-store-sync.log 2>&1
```

### 配置要同步的仓库

编辑 `backend/scripts/sync_data.py` 中的 `REPOS_TO_SYNC` 列表：

```python
REPOS_TO_SYNC = [
    # 格式: "owner/repo"
    "nickcyber-team/github-releases-store",
    "microsoft/vscode",
    "obsidianmd/obsidian-releases",
    # 添加更多仓库...
]
```

---

## 常见问题

### 1. 数据库连接失败

```
错误: connection refused
```

**解决方法**:
- 检查 PostgreSQL 是否运行: `sudo systemctl status postgresql`
- 检查连接参数是否正确
- 检查 PostgreSQL 是否允许远程连接（如需要）

### 2. CORS 错误

```
错误: Access-Control-Allow-Origin
```

**解决方法**:
- 检查 `BACKEND_CORS_ORIGINS` 是否包含前端地址
- 确保 URL 格式正确（包含协议和端口）

### 3. GitHub API 限流

```
错误: API rate limit exceeded
```

**解决方法**:
- 确保配置了有效的 `GITHUB_TOKEN`
- 减少同步频率
- 使用 GitHub App 获取更高的限额

### 4. 前端构建失败

```
错误: Node.js version not supported
```

**解决方法**:
- 确保 Node.js 版本 >= 20.19.0
- 使用 nvm 管理 Node.js 版本: `nvm install 22`

### 5. Tailwind CSS 样式不生效

**解决方法**:
- 确保 `@tailwindcss/vite` 插件已安装
- 检查 `main.css` 是否包含 `@import "tailwindcss"`
- 清除缓存重新构建: `npm run build -- --force`

### 6. 数据库迁移失败

**解决方法**:
```bash
# 查看当前迁移状态
alembic current

# 查看迁移历史
alembic history

# 回滚到上一版本
alembic downgrade -1

# 重新迁移
alembic upgrade head
```

---

## 安全建议

1. **生产环境必须更改默认密钥**
   - `SECRET_KEY` 使用强随机值
   - 数据库密码使用强密码

2. **启用 HTTPS**
   - 使用 Let's Encrypt 获取免费证书
   - 配置 Nginx SSL

3. **限制数据库访问**
   - 只允许应用服务器连接
   - 不要暴露数据库端口

4. **定期备份**
   - 设置数据库自动备份
   - 备份存储到远程位置

5. **监控和日志**
   - 配置日志收集
   - 设置告警规则

---

## 技术支持

如遇到问题，请：

1. 查看日志文件排查错误
2. 检查 GitHub Issues 是否有类似问题
3. 创建新的 Issue 描述问题
