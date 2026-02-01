# GitHub Releases Store - 部署快速参考

## 目录

1. [ECS 首次部署](#ecs-首次部署)
2. [日常维护](#日常维护)
3. [故障排查](#故障排查)
4. [数据管理](#数据管理)
5. [更新升级](#更新升级)

---

## ECS 首次部署

### 1. 准备服务器

```bash
# 登录 ECS
ssh root@your-ecs-ip

# 一键安装（推荐）
curl -fsSL https://raw.githubusercontent.com/your-repo/github-store-web/main/scripts/ecs-setup.sh | sudo bash

# 或手动部署
apt update && apt install -y docker.io docker-compose git
```

### 2. 配置和部署

```bash
cd /opt/github-store-web

# 编辑环境变量
vim .env.production

# 部署
docker-compose -f docker-compose.prod.yml up -d --build

# 数据库迁移
docker-compose -f docker-compose.prod.yml exec data-service alembic upgrade head

# 初始数据同步
./scripts/sync.sh --popular
```

### 3. 访问验证

```bash
# 健康检查
curl http://localhost/health

# 查看状态
docker-compose -f docker-compose.prod.yml ps
```

---

## 日常维护

### 查看状态

```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml top
docker stats
```

### 查看日志

```bash
# 所有服务
docker-compose -f docker-compose.prod.yml logs -f

# 指定服务
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f data-celery-worker
docker-compose -f docker-compose.prod.yml logs -f nginx

# 最近 100 行
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 重启服务

```bash
# 重启所有
docker-compose -f docker-compose.prod.yml restart

# 重启单个服务
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart nginx

# 使用部署脚本（推荐）
./deploy_prod.sh --skip-build
```

---

## 故障排查

### 服务无法启动

```bash
# 查看错误日志
docker-compose -f docker-compose.prod.yml logs [service-name]

# 检查端口占用
netstat -tlnp | grep 80
lsof -i :80

# 重建镜像
docker-compose -f docker-compose.prod.yml build --no-cache
```

### 数据库问题

```bash
# 连接数据库
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d github_store

# 查看迁移状态
docker-compose -f docker-compose.prod.yml exec data-service alembic current
docker-compose -f docker-compose.prod.yml exec data-service alembic history

# 回滚迁移
docker-compose -f docker-compose.prod.yml exec data-service alembic downgrade -1
```

### 网络问题

```bash
# 测试内部网络
docker-compose -f docker-compose.prod.yml exec nginx ping backend -c 3
docker-compose -f docker-compose.prod.yml exec backend ping db -c 3

# 查看网络
docker network ls
docker network inspect github-store-web_app-network
```

### 性能问题

```bash
# 查看资源使用
docker stats --no-stream
top
htop

# 查看磁盘空间
df -h
du -sh /var/lib/docker

# 查看内存
free -h
cat /proc/meminfo
```

---

## 数据管理

### 手动备份

```bash
# 使用脚本
./scripts/backup.sh

# 手动备份
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres github_store | gzip > backup_$(date +%Y%m%d).sql.gz
```

### 恢复数据

```bash
# 停止相关服务
docker-compose -f docker-compose.prod.yml stop backend data-service

# 恢复数据库
gunzip < backup_20240101.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres -d github_store

# 启动服务
docker-compose -f docker-compose.prod.yml start backend data-service
```

### 数据同步

```bash
# 快速同步（热门仓库）
./scripts/sync.sh --popular

# 完整同步
./scripts/sync.sh --full

# 限制数量
./scripts/sync.sh --full --limit 5

# 手动执行
docker-compose -f docker-compose.prod.yml exec data-service python scripts/sync_data.py --popular-only
```

### 查看数据库大小

```bash
# 数据库大小
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('github_store'));"

# 表大小
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d github_store -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname='public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

## 更新升级

### 代码更新

```bash
cd /opt/github-store-web

# 拉取最新代码
git pull

# 标准更新（保留数据）
./deploy_prod.sh

# 快速重启（不重建）
./deploy_prod.sh --skip-build
```

### 配置更新

```bash
# 修改配置后重载
vim .env.production
docker-compose -f docker-compose.prod.yml up -d

# 或者完全重启
docker-compose -f docker-compose.prod.yml restart
```

### 全新部署（清空数据）

```bash
# ⚠️ 警告：这将删除所有数据！
./deploy_prod.sh --fresh
```

---

## 常用命令速查表

| 操作 | 命令 |
|------|------|
| 启动服务 | `docker-compose -f docker-compose.prod.yml up -d` |
| 停止服务 | `docker-compose -f docker-compose.prod.yml down` |
| 查看日志 | `docker-compose -f docker-compose.prod.yml logs -f` |
| 进入容器 | `docker-compose -f docker-compose.prod.yml exec [service] bash` |
| 查看资源 | `docker stats` |
| 数据库迁移 | `docker-compose -f docker-compose.prod.yml exec data-service alembic upgrade head` |
| 数据同步 | `./scripts/sync.sh --popular` |
| 备份 | `./scripts/backup.sh` |

---

## 文件路径

| 文件 | 路径 |
|------|------|
| 项目目录 | `/opt/github-store-web` |
| 环境配置 | `/opt/github-store-web/.env.production` |
| Nginx 配置 | `/opt/github-store-web/nginx/nginx.conf` |
| 备份目录 | `/backups/github-store` |
| Docker 数据 | `/var/lib/docker/volumes/` |

---

## 获取帮助

```bash
# 脚本帮助
./deploy_prod.sh --help
./scripts/sync.sh --help

# 查看文档
cat docs/ecs-deployment-guide.md
cat docs/deployment-quick-reference.md
```
