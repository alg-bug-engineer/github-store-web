# 火山引擎 ECS 部署及本地联调指南

本文档提供了在火山引擎（Volcano Engine）ECS 服务器上部署 `github-store-web` 应用，以及如何配置本地开发环境以连接远程数据库进行调试的具体步骤。

## 目录
1. [在火山引擎 ECS 上部署](#第-1-部分在火山引擎-ecs-上部署)
    - [步骤 1：准备 ECS 环境](#步骤-1准备-ecs-环境)
    - [步骤 2：获取并配置项目](#步骤-2获取并配置项目)
    - [步骤 3：构建并运行应用](#步骤-3构建并运行应用)
    - [步骤 4：执行数据库迁移](#步骤-4执行数据库迁移)
2. [本地联调测试](#第-2-部分本地联调测试)
    - [步骤 1：在 ECS 上暴露数据库端口](#步骤-1在-ecs-上暴露数据库端口)
    - [步骤 2：配置本地 data-service](#步骤-2配置本地-data-service)
    - [步骤 3：在本地运行 data-service](#步骤-3在本地运行-data-service)

---

### 第 1 部分：在火山引擎 ECS 上部署

本教程将指导你使用 Docker 和 Docker Compose 在火山引擎的 ECS 服务器上部署整个应用。

#### 步骤 1：准备 ECS 环境

1.  **连接服务器**: 通过 SSH 登录到你的火山引擎 ECS 实例。
2.  **安装 Docker**: 如果你的服务器上没有安装 Docker，请参照官方文档进行安装。
    ```bash
    # 便利贴：安装 Docker
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
    ```
3.  **安装 Docker Compose**:
    ```bash
    # 便利贴：安装 Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```

#### 步骤 2：获取并配置项目

1.  **克隆代码**:
    ```bash
    git clone <你的项目git地址>
    cd github-store-web # 进入项目根目录
    ```
2.  **创建配置文件**: `docker-compose.prod.yml` 文件通过环境变量来加载敏感配置。你需要在项目根目录下创建一个 `.env` 文件。
    ```bash
    touch .env
    ```
    然后编辑这个 `.env` 文件，填入以下内容。**请务必替换为你自己的真实密码和令牌。**

    ```ini
    # .env 文件内容

    # 数据库配置
    POSTGRES_PASSWORD=your_strong_and_secret_password # 设置一个健壮的数据库密码
    POSTGRES_USER=postgres
    POSTGRES_DB=github_store

    # GitHub API 令牌
    # 用于 data-service 从 GitHub 拉取数据
    GITHUB_TOKEN=your_github_personal_access_token

    # 后端 API 服务配置
    # 用于 JWT 令牌签名的密钥
    SECRET_KEY=your_very_secret_key_for_jwt
    # Kimi API (可选)
    KIMI_API_KEY=
    # 允许的跨域来源 (示例)
    BACKEND_CORS_ORIGINS=["http://your.domain.com","https://your.domain.com"]

    # Nginx 端口
    HTTP_PORT=80
    HTTPS_PORT=443

    # 前端配置 (VITE_API_BASE_URL 默认在 compose 文件中设置了, 此处可覆盖)
    VITE_API_BASE_URL=/api/v1
    ```

#### 步骤 3：构建并运行应用

1.  **启动服务**: 在项目根目录中，执行以下命令来构建镜像并以“分离模式”（-d）在后台启动所有服务。
    ```bash
    docker-compose -f docker-compose.prod.yml up -d --build
    ```
    这个命令会：
    *   `--build`: 强制重新构建所有服务的 Docker 镜像。
    *   `-d`: 在后台运行容器。

2.  **验证**: 等待几分钟，让所有服务完成启动。然后使用 `docker-compose ps` 查看所有容器的状态，确保它们都处于 `Up` 或 `running` 状态。

#### 步骤 4：执行数据库迁移

首次启动时，数据库是空的。你需要运行数据库迁移脚本来创建所有数据表。`data-service` 使用了 Alembic 进行迁移管理。

1.  **执行迁移**:
    ```bash
    docker-compose -f docker-compose.prod.yml exec data-service alembic upgrade head
    ```
2.  **数据同步**: `data-service` 包含一个用于同步 GitHub 数据的 Celery 任务。在迁移完成后，这个后台任务会自动开始从 GitHub 拉取数据并存入数据库。你可以通过查看日志来监控进度：
    ```bash
    docker-compose -f docker-compose.prod.yml logs -f data-celery-worker
    ```

部署完成后，你应该可以通过 ECS 的公网 IP 地址在浏览器中访问你的应用。Nginx 会处理请求并将其转发到前端或后端服务。

---

### 第 2 部分：本地联调测试

本节介绍如何将你本地的 `data-service` 连接到运行在 ECS 上的数据库，以便进行调试。

#### 步骤 1：在 ECS 上暴露数据库端口

**⚠️ 安全警告**: 将数据库端口直接暴露到公网上存在巨大安全风险，任何知道你 IP 地址的人都可以尝试访问它。**强烈建议**你仅为临时调试执行此操作，并配置火山引擎的安全组规则，只允许你自己的本地 IP 地址访问该端口。更好的长期方案是使用 SSH 隧道或 VPN。

1.  **修改 Docker Compose 文件**: 在 ECS 上，编辑 `docker-compose.prod.yml` 文件。找到 `db` 服务，添加一个 `ports` 映射。
    ```yaml
    # ... other services
    db:
      image: postgres:15-alpine
      restart: always
      ports: # <--- 添加这部分
        - "5432:5432" # 将容器的 5432 端口映射到主机的 5432 端口
      environment:
    # ... rest of the db service
    ```
2.  **重启服务**: 保存文件后，在 ECS 上重新启动 docker-compose 以应用更改。
    ```bash
    docker-compose -f docker-compose.prod.yml up -d --no-deps db
    ```

#### 步骤 2：配置本地 `data-service`

1.  **安装依赖**: 在你本地的开发机上，进入 `data-service` 目录，并为该服务创建一个独立的 Python 虚拟环境并安装依赖。
    ```bash
    cd data-service
    python -m venv venv
    source venv/bin/activate  # on Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
2.  **创建本地配置文件**: 在 `data-service` 目录下创建一个名为 `.env` 的文件。
    ```bash
    touch .env
    ```
    编辑这个文件，设置 `DATABASE_URL` 指向你在 ECS 上运行的数据库。
    ```ini
    # data-service/.env
    # 将 YOUR_ECS_PUBLIC_IP 替换为你的 ECS 公网 IP 地址
    # 将 your_strong_and_secret_password 替换为你在 ECS 上 .env 文件中设置的密码
    DATABASE_URL=postgresql://postgres:your_strong_and_secret_password@YOUR_ECS_PUBLIC_IP:5432/github_store

    # 本地运行时也需要 GITHUB_TOKEN
    GITHUB_TOKEN=your_github_personal_access_token
    ```

#### 步骤 3：在本地运行 `data-service`

1.  **启动服务**: 在 `data-service` 目录下，确保你的虚拟环境已激活，然后使用 uvicorn 启动服务。
    ```bash
    # 确保虚拟环境已激活
    uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
    ```
    `--reload` 参数会使服务在代码变更时自动重启，非常适合开发。

现在，你本地运行的 `data-service` 实例就会连接到 ECS 上的 PostgreSQL 数据库了。你可以在本地修改代码、设置断点进行调试，所有数据库操作都会反映在远程数据库中。

联调完成后，请务必**移除 ECS 上 `docker-compose.prod.yml` 文件中暴露的端口**并重启服务，以关闭数据库的公网访问。
