# 部署脚本说明

此目录包含用于 ECS 部署和维护的实用脚本。

## 脚本列表

### 1. ecs-setup.sh

**用途**: ECS 服务器一键部署脚本

**使用方法**:
```bash
# 下载脚本并执行
chmod +x scripts/ecs-setup.sh
sudo ./scripts/ecs-setup.sh
```

**功能**:
- 自动更新系统
- 安装 Docker 和 Docker Compose
- 配置防火墙（UFW）
- 克隆项目代码
- 生成环境变量配置
- 部署所有服务
- 执行数据库迁移

---

### 2. backup.sh

**用途**: 数据库备份脚本

**使用方法**:
```bash
# 备份到默认目录 (/backups/github-store)
./scripts/backup.sh

# 备份到指定目录
./scripts/backup.sh /path/to/backup
```

**功能**:
- 备份 PostgreSQL 数据库
- 自动压缩备份文件
- 自动清理 7 天前的旧备份
- 显示备份文件大小

**定时备份示例**:
```bash
# 每天凌晨 2 点自动备份
crontab -e
# 添加以下行
0 2 * * * /opt/github-store-web/scripts/backup.sh
```

---

### 3. sync.sh

**用途**: 数据同步脚本

**使用方法**:
```bash
# 显示帮助
./scripts/sync.sh --help

# 快速同步（仅热门仓库，推荐首次使用）
./scripts/sync.sh --popular

# 完整同步
./scripts/sync.sh --full

# 完整同步，限制数量
./scripts/sync.sh --full --limit 5
```

**功能**:
- 触发 GitHub 数据同步
- 支持快速模式（仅预定义仓库）
- 支持限制同步数量
- 自动检查服务状态

---

## 快速部署流程

```bash
# 1. 登录 ECS 服务器
ssh root@your-ecs-ip

# 2. 下载并执行部署脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/github-store-web/main/scripts/ecs-setup.sh | sudo bash

# 或者手动执行
git clone https://github.com/your-repo/github-store-web.git
cd github-store-web
sudo ./scripts/ecs-setup.sh

# 3. 编辑环境变量配置
vim .env.production
# 填入 GitHub Token 和其他配置

# 4. 重新加载配置
docker-compose -f docker-compose.prod.yml up -d

# 5. 执行数据同步
./scripts/sync.sh --popular

# 6. 设置定时备份
crontab -e
# 添加: 0 2 * * * /opt/github-store-web/scripts/backup.sh
```

## 注意事项

1. **权限**: 部分脚本需要 root 权限运行
2. **路径**: 脚本默认在项目根目录执行，确保路径正确
3. **Docker**: 确保 Docker 和 Docker Compose 已安装
4. **备份**: 建议定期备份数据库，特别是生产环境
