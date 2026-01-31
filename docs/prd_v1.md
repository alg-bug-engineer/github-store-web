# GitHub Releases Store - 系统设计文档 v1.0

## 📋 文档信息

- **项目名称**: GitHub Releases Store
- **版本**: 1.0
- **文档类型**: 技术设计文档
- **创建日期**: 2026-01-29
- **目标用户**: 非技术用户群体

---

## 🎯 一、产品定位与核心目标

### 1.1 产品定位
为非技术用户提供简单、易懂的 GitHub 开源应用发现和下载平台，降低使用开源软件的门槛。

### 1.2 核心价值
- **易懂性**: 将技术术语转化为通俗语言
- **可靠性**: 通过缓存机制确保服务稳定
- **智能性**: AI 助手引导用户发现和使用应用
- **便捷性**: 简化下载流程，直达目标

### 1.3 非目标
- ❌ 不做应用管理工具
- ❌ 不做社区论坛
- ❌ 不做企业级功能
- ❌ 不依赖用户 GitHub 账号

---

## 🏗️ 二、系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Web浏览器 │  │  H5页面  │  │  游客    │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                         ↓ HTTPS
┌─────────────────────────────────────────────────────────┐
│                    应用服务层                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Nginx (反向代理/负载均衡)              │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Web服务     │  │  API服务     │  │ Kimi集成    │  │
│  │  (静态资源)  │  │  (业务逻辑)  │  │ (AI助手)    │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    数据层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ PostgreSQL   │  │  Redis       │  │  文件存储   │  │
│  │ (主数据库)   │  │  (缓存)      │  │  (日志等)   │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    外部服务层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ GitHub API   │  │  短信服务    │  │  CDN加速    │  │
│  │              │  │  (阿里云等)  │  │             │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 技术栈选型

#### 后端技术栈
```
框架层:
- Python 3.11+ (主语言)
- FastAPI (Web 框架，异步高性能)
- SQLAlchemy 2.0 (ORM)
- Pydantic (数据验证)

数据存储:
- PostgreSQL 15+ (主数据库)
- Redis 7.0+ (缓存)
- MinIO/阿里云OSS (对象存储，可选)

任务调度:
- Celery + Redis (异步任务)
- APScheduler (定时任务)

监控日志:
- Prometheus + Grafana (监控)
- ELK Stack (日志分析，可选)
```

#### 前端技术栈
```
核心框架:
- HTML5 + CSS3 + JavaScript ES6+
- 或 Vue 3 + Vite (考虑后续扩展)

UI组件:
- 自定义组件库 (GitHub风格)
- Tailwind CSS (样式框架，可选)

API调用:
- Fetch API / Axios
- WebSocket (实时通知)
```

---

## 🗄️ 三、数据库设计

### 3.1 PostgreSQL 表结构设计

#### 3.1.1 用户表 (users)
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,              -- 手机号
    password_hash VARCHAR(255) NOT NULL,            -- 密码哈希
    nickname VARCHAR(50),                           -- 昵称
    avatar_url VARCHAR(255),                        -- 头像URL
    status SMALLINT DEFAULT 1,                      -- 状态: 1正常 0禁用
    last_login_at TIMESTAMP,                        -- 最后登录时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_phone (phone),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- 用户会话表 (sessions)
CREATE TABLE user_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    token VARCHAR(64) UNIQUE NOT NULL,              -- 会话token
    device_info JSONB,                              -- 设备信息
    ip_address INET,                                -- IP地址
    expires_at TIMESTAMP NOT NULL,                  -- 过期时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_token (token),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);
```

#### 3.1.2 项目缓存表 (repositories)
```sql
CREATE TABLE repositories (
    id BIGSERIAL PRIMARY KEY,
    full_name VARCHAR(255) UNIQUE NOT NULL,         -- owner/repo
    owner VARCHAR(100) NOT NULL,                    -- 所有者
    name VARCHAR(100) NOT NULL,                     -- 仓库名
    description TEXT,                               -- 描述
    homepage VARCHAR(255),                          -- 主页
    
    -- GitHub 数据
    github_id BIGINT UNIQUE,                        -- GitHub仓库ID
    html_url VARCHAR(255),                          -- GitHub URL
    avatar_url VARCHAR(255),                        -- 头像URL
    
    -- 统计数据
    stars INTEGER DEFAULT 0,                        -- Star数
    forks INTEGER DEFAULT 0,                        -- Fork数
    watchers INTEGER DEFAULT 0,                     -- Watch数
    open_issues INTEGER DEFAULT 0,                  -- 开放Issue数
    
    -- 分类信息
    language VARCHAR(50),                           -- 主要语言
    topics TEXT[],                                  -- 主题标签
    category VARCHAR(50),                           -- 分类: android/desktop/tools等
    
    -- 状态信息
    has_releases BOOLEAN DEFAULT FALSE,             -- 是否有Release
    is_archived BOOLEAN DEFAULT FALSE,              -- 是否归档
    is_active BOOLEAN DEFAULT TRUE,                 -- 是否活跃
    
    -- 更新策略
    update_priority SMALLINT DEFAULT 2,             -- 更新优先级: 1热门 2活跃 3普通 4冷门
    next_update_at TIMESTAMP,                       -- 下次更新时间
    
    -- 时间戳
    github_created_at TIMESTAMP,                    -- GitHub创建时间
    github_updated_at TIMESTAMP,                    -- GitHub更新时间
    last_synced_at TIMESTAMP,                       -- 最后同步时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_full_name (full_name),
    INDEX idx_category (category),
    INDEX idx_language (language),
    INDEX idx_stars (stars DESC),
    INDEX idx_update_priority (update_priority),
    INDEX idx_next_update_at (next_update_at),
    INDEX idx_has_releases (has_releases),
    INDEX idx_is_active (is_active)
);
```

#### 3.1.3 Release 信息表 (releases)
```sql
CREATE TABLE releases (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    
    -- Release 基本信息
    github_release_id BIGINT UNIQUE,                -- GitHub Release ID
    tag_name VARCHAR(100) NOT NULL,                 -- 版本标签
    name VARCHAR(255),                              -- Release名称
    body TEXT,                                      -- 更新日志
    
    -- 版本状态
    is_prerelease BOOLEAN DEFAULT FALSE,            -- 是否预发布
    is_draft BOOLEAN DEFAULT FALSE,                 -- 是否草稿
    is_latest BOOLEAN DEFAULT FALSE,                -- 是否最新版本
    
    -- 时间信息
    published_at TIMESTAMP,                         -- 发布时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_repo_id (repo_id),
    INDEX idx_tag_name (tag_name),
    INDEX idx_is_latest (is_latest),
    INDEX idx_published_at (published_at DESC)
);
```

#### 3.1.4 下载文件表 (release_assets)
```sql
CREATE TABLE release_assets (
    id BIGSERIAL PRIMARY KEY,
    release_id BIGINT NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
    
    -- 文件信息
    github_asset_id BIGINT UNIQUE,                  -- GitHub Asset ID
    name VARCHAR(255) NOT NULL,                     -- 文件名
    label VARCHAR(255),                             -- 标签
    content_type VARCHAR(100),                      -- MIME类型
    size BIGINT,                                    -- 文件大小(字节)
    
    -- 下载信息
    browser_download_url TEXT NOT NULL,             -- 下载URL
    download_count INTEGER DEFAULT 0,               -- 下载次数(GitHub统计)
    
    -- 文件分类
    platform VARCHAR(50),                           -- 平台: android/windows/linux/macos
    file_type VARCHAR(20),                          -- 文件类型: apk/exe/dmg/deb/rpm等
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_release_id (release_id),
    INDEX idx_platform (platform),
    INDEX idx_file_type (file_type),
    INDEX idx_name (name)
);
```

#### 3.1.5 README 缓存表 (readme_cache)
```sql
CREATE TABLE readme_cache (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT UNIQUE NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    
    -- README 内容
    content TEXT,                                   -- 原始内容
    html_content TEXT,                              -- HTML渲染内容
    encoding VARCHAR(20),                           -- 编码方式
    
    -- 时间戳
    synced_at TIMESTAMP,                            -- 同步时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_repo_id (repo_id)
);
```

#### 3.1.6 用户收藏表 (user_favorites)
```sql
CREATE TABLE user_favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    repo_id BIGINT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    
    -- 收藏信息
    note TEXT,                                      -- 用户备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, repo_id),
    INDEX idx_user_id (user_id),
    INDEX idx_repo_id (repo_id),
    INDEX idx_created_at (created_at DESC)
);
```

#### 3.1.7 搜索历史表 (search_history)
```sql
CREATE TABLE search_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,  -- NULL表示游客
    
    -- 搜索信息
    query TEXT NOT NULL,                            -- 搜索关键词
    filters JSONB,                                  -- 过滤条件
    result_count INTEGER,                           -- 结果数量
    
    -- 元数据
    ip_address INET,                                -- IP地址
    user_agent TEXT,                                -- User Agent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_query (query),
    INDEX idx_created_at (created_at DESC)
);
```

#### 3.1.8 推荐配置表 (recommendations)
```sql
CREATE TABLE recommendations (
    id BIGSERIAL PRIMARY KEY,
    
    -- 推荐类型
    type VARCHAR(50) NOT NULL,                      -- 类型: editor_choice/trending/new等
    title VARCHAR(255) NOT NULL,                    -- 推荐标题
    description TEXT,                               -- 推荐描述
    
    -- 推荐内容
    repo_ids BIGINT[],                              -- 推荐的仓库ID列表
    display_order INTEGER DEFAULT 0,                -- 显示顺序
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,                 -- 是否启用
    start_at TIMESTAMP,                             -- 开始时间
    end_at TIMESTAMP,                               -- 结束时间
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_type (type),
    INDEX idx_is_active (is_active),
    INDEX idx_display_order (display_order)
);
```

#### 3.1.9 系统配置表 (system_configs)
```sql
CREATE TABLE system_configs (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,               -- 配置键
    value JSONB NOT NULL,                           -- 配置值(JSON格式)
    description TEXT,                               -- 配置说明
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_key (key)
);

-- 初始化配置
INSERT INTO system_configs (key, value, description) VALUES
('update_intervals', '{
    "hot_projects": 300,
    "active_projects": 600,
    "normal_projects": 1800,
    "cold_projects": 3600
}'::jsonb, '项目更新时间间隔(秒)'),
('github_token', '{"token": "ghp_xxxxx"}'::jsonb, 'GitHub API Token'),
('kimi_api', '{"api_key": "xxx", "endpoint": "https://api.moonshot.cn"}'::jsonb, 'Kimi API配置'),
('search_filters', '{
    "android": "topic:android stars:>50 archived:false",
    "desktop": "topic:desktop stars:>50 archived:false",
    "popular": "stars:>500 archived:false"
}'::jsonb, '搜索过滤器配置');
```

### 3.2 Redis 缓存设计

#### 3.2.1 缓存键命名规范
```
格式: {namespace}:{type}:{identifier}:{field}

示例:
- repo:list:android:page_1          # Android应用列表第1页
- repo:detail:owner/name            # 仓库详情
- release:latest:owner/name         # 最新Release
- search:result:keyword_hash        # 搜索结果
- user:session:token_xxx            # 用户会话
- api:quota:remaining               # API配额剩余
```

#### 3.2.2 缓存策略表
```
| 键前缀 | 数据类型 | 过期时间 | 说明 |
|--------|---------|---------|------|
| repo:list:* | String(JSON) | 1小时 | 项目列表 |
| repo:detail:* | Hash | 30分钟 | 项目详情 |
| release:latest:* | String(JSON) | 10分钟 | 最新Release |
| release:list:* | String(JSON) | 30分钟 | Release列表 |
| search:result:* | String(JSON) | 1小时 | 搜索结果 |
| user:session:* | String(JSON) | 7天 | 用户会话 |
| api:quota:* | String | 1小时 | API配额 |
| hot:projects | ZSet | 1小时 | 热门项目(按Stars排序) |
| trending:daily | List | 1天 | 每日趋势 |
```

---

## 🔧 四、核心功能模块设计

### 4.1 数据同步模块

#### 4.1.1 定时同步任务设计

```python
# 伪代码示例
class RepositorySyncScheduler:
    """仓库同步调度器"""
    
    def schedule_sync_tasks(self):
        """根据优先级调度同步任务"""
        
        # 获取需要更新的仓库列表
        repos = self.get_repos_to_update()
        
        for repo in repos:
            # 根据优先级确定更新间隔
            interval = self.get_update_interval(repo.update_priority)
            
            # 判断是否到达更新时间
            if repo.next_update_at <= now():
                # 异步执行同步任务
                sync_repository_task.delay(repo.id)
                
                # 更新下次同步时间
                repo.next_update_at = now() + interval
                repo.save()
    
    def get_update_interval(self, priority):
        """获取更新间隔"""
        intervals = {
            1: 300,   # 热门项目: 5分钟
            2: 600,   # 活跃项目: 10分钟
            3: 1800,  # 普通项目: 30分钟
            4: 3600   # 冷门项目: 1小时
        }
        return intervals.get(priority, 1800)
```

#### 4.1.2 智能优先级调整

```python
def adjust_repository_priority(repo):
    """动态调整仓库更新优先级"""
    
    # 热门项目 (Stars > 10000)
    if repo.stars > 10000:
        return 1
    
    # 活跃项目 (最近7天有Release)
    recent_release = repo.releases.filter(
        published_at >= now() - timedelta(days=7)
    ).exists()
    if recent_release:
        return 2
    
    # 普通项目 (最近30天有更新)
    if repo.github_updated_at >= now() - timedelta(days=30):
        return 3
    
    # 冷门项目 (长期无更新)
    return 4
```

#### 4.1.3 GitHub API 调用封装

```python
class GitHubAPIClient:
    """GitHub API 客户端"""
    
    def __init__(self):
        self.token = self.load_token_from_db()
        self.base_url = "https://api.github.com"
        self.rate_limit_remaining = None
    
    async def search_repositories(self, query, page=1):
        """搜索仓库"""
        
        # 检查API配额
        if not self.check_rate_limit():
            raise RateLimitExceeded("API配额已用尽")
        
        # 调用GitHub API
        response = await self.request(
            "GET",
            "/search/repositories",
            params={"q": query, "page": page, "per_page": 30}
        )
        
        # 更新配额信息
        self.update_rate_limit(response.headers)
        
        return response.json()
    
    async def get_repository(self, owner, repo):
        """获取仓库详情"""
        # 先检查缓存
        cache_key = f"repo:detail:{owner}/{repo}"
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # API请求
        response = await self.request("GET", f"/repos/{owner}/{repo}")
        data = response.json()
        
        # 写入缓存
        await redis.setex(cache_key, 1800, json.dumps(data))
        
        return data
    
    def check_rate_limit(self):
        """检查API配额"""
        # 从Redis获取配额信息
        remaining = redis.get("api:quota:remaining")
        if remaining and int(remaining) > 100:
            return True
        
        # 实时查询配额
        response = self.request("GET", "/rate_limit")
        self.rate_limit_remaining = response.json()["rate"]["remaining"]
        
        # 缓存配额信息
        redis.setex("api:quota:remaining", 3600, self.rate_limit_remaining)
        
        return self.rate_limit_remaining > 100
```

### 4.2 用户认证模块

#### 4.2.1 注册流程

```
用户注册流程:
1. 输入手机号
2. 发送短信验证码
3. 验证验证码
4. 设置密码(6-20位,包含字母和数字)
5. 设置昵称(可选)
6. 注册成功,自动登录

数据校验:
- 手机号: 中国大陆11位手机号
- 密码: 6-20位,必须包含字母和数字
- 验证码: 6位数字,5分钟有效
```

#### 4.2.2 登录流程

```
登录方式:
1. 手机号+密码登录
2. 手机号+验证码登录(忘记密码时)

会话管理:
- 登录成功后生成 session_token
- token 有效期: 7天
- 支持多设备同时登录
- 提供"记住我"选项(30天有效期)
```

#### 4.2.3 游客模式

```
游客权限:
✅ 浏览项目列表
✅ 查看项目详情
✅ 下载应用
✅ 使用AI助手(有限次数)
❌ 收藏项目
❌ 查看收藏列表
❌ 保存搜索历史

限制策略:
- 单IP每小时最多20次搜索
- AI助手每天最多5次对话
- 提示注册获得完整功能
```

### 4.3 搜索与过滤模块

#### 4.3.1 搜索接口设计

```
GET /api/v1/search

参数:
- q: 搜索关键词
- category: 分类(android/desktop/tools/all)
- language: 编程语言
- sort: 排序(stars/updated/created)
- page: 页码
- per_page: 每页数量(默认20,最大50)

返回:
{
    "total": 100,
    "page": 1,
    "per_page": 20,
    "items": [
        {
            "id": 1,
            "full_name": "owner/repo",
            "name": "应用名称",
            "description": "简单描述",
            "category": "android",
            "language": "Kotlin",
            "stars": 1000,
            "latest_version": "v1.0.0",
            "avatar_url": "https://...",
            "topics": ["android", "open-source"]
        }
    ]
}
```

#### 4.3.2 预设过滤器

```python
# 配置化的过滤器
FILTER_PRESETS = {
    "android": {
        "query": "topic:android stars:>50 archived:false",
        "category": "android",
        "display_name": "Android 应用"
    },
    "desktop": {
        "query": "topic:desktop stars:>50 archived:false",
        "category": "desktop",
        "display_name": "桌面应用"
    },
    "popular": {
        "query": "stars:>500 archived:false",
        "sort": "stars",
        "display_name": "热门项目"
    },
    "trending": {
        "query": "created:>2024-01-01 stars:>100",
        "sort": "stars",
        "display_name": "新兴项目"
    }
}
```

### 4.4 Kimi AI 助手模块

#### 4.4.1 集成方案

```python
class KimiAIAssistant:
    """Kimi AI 助手"""
    
    def __init__(self):
        self.api_key = self.load_from_config()
        self.endpoint = "https://api.moonshot.cn/v1/chat/completions"
    
    async def chat(self, user_message, context=None):
        """对话接口"""
        
        # 构建系统提示词
        system_prompt = self.build_system_prompt(context)
        
        # 调用Kimi API
        response = await self.call_kimi_api(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        
        return response["choices"][0]["message"]["content"]
    
    def build_system_prompt(self, context):
        """构建系统提示词"""
        
        prompt = """你是一个开源应用助手,帮助用户发现和使用GitHub上的优质应用。

你的职责:
1. 理解用户需求,推荐合适的应用
2. 用通俗易懂的语言解释技术概念
3. 提供下载和安装指导
4. 回答应用相关问题

回答原则:
- 语言简洁友好,避免技术术语
- 优先推荐安全、活跃的项目
- 如果不确定,诚实说明
- 每次最多推荐3个应用
"""
        
        # 添加上下文(当前页面的项目列表)
        if context:
            prompt += f"\n当前页面项目:\n{context}"
        
        return prompt
```

#### 4.4.2 使用场景设计

```
场景1: 推荐应用
用户: "我想找一个安卓音乐播放器"
AI: "为您推荐以下音乐播放器:
    1. Phonograph - 轻量级,Material Design风格
    2. VLC for Android - 功能强大,支持多种格式
    3. BlackHole - 开源无广告,支持在线音乐
    
    点击查看详情和下载链接。"

场景2: 安装指导
用户: "这个APK怎么安装?"
AI: "安装步骤:
    1. 在手机设置中允许'未知来源'应用
    2. 下载APK文件
    3. 点击文件进行安装
    4. 按提示完成安装
    
    需要详细图文教程吗?"

场景3: 应用对比
用户: "Termux和UserLAnd哪个好?"
AI: "两者都是安卓终端应用:
    Termux: 更轻量,命令行为主,适合熟悉Linux的用户
    UserLAnd: 带图形界面,更易上手,适合新手
    
    根据您的需求,我推荐..."

场景4: 问题解答
用户: "这个应用安全吗?"
AI: "根据项目信息:
    ✅ 开源代码,可审查
    ✅ 1000+ Stars,社区认可
    ✅ 最近更新活跃
    ⚠️ 需要存储和网络权限
    
    总体来说是安全的,您可以放心使用。"
```

#### 4.4.3 数据访问权限设计

```python
# AI助手可访问的数据接口
class AIDataAccess:
    """为AI助手提供数据访问"""
    
    async def get_project_list(self, category=None, limit=10):
        """获取项目列表(供AI推荐)"""
        query = db.query(Repository).filter(
            Repository.is_active == True,
            Repository.has_releases == True
        )
        
        if category:
            query = query.filter(Repository.category == category)
        
        return query.order_by(Repository.stars.desc()).limit(limit).all()
    
    async def search_projects(self, keyword, limit=5):
        """搜索项目(供AI查询)"""
        # 全文搜索
        results = await self.full_text_search(keyword, limit)
        
        # 格式化返回数据
        return [
            {
                "name": r.name,
                "description": r.description,
                "stars": r.stars,
                "category": r.category
            }
            for r in results
        ]
    
    async def get_project_detail(self, full_name):
        """获取项目详情(供AI解答)"""
        repo = await Repository.get_by_full_name(full_name)
        
        return {
            "name": repo.name,
            "description": repo.description,
            "stars": repo.stars,
            "language": repo.language,
            "latest_version": repo.latest_release.tag_name,
            "has_releases": repo.has_releases,
            "is_active": repo.is_active
        }
```

### 4.5 发现与推荐模块

#### 4.5.1 页面布局设计

```
┌────────────────────────────────────────┐
│           顶部Banner                    │
│     (每日推荐/编辑精选/活动推广)        │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│   🔥 热门推荐                           │
│   ┌──────┐ ┌──────┐ ┌──────┐          │
│   │App 1 │ │App 2 │ │App 3 │  →更多    │
│   └──────┘ └──────┘ └──────┘          │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│   📱 Android 应用                       │
│   ┌──────┐ ┌──────┐ ┌──────┐          │
│   │App 1 │ │App 2 │ │App 3 │  →更多    │
│   └──────┘ └──────┘ └──────┘          │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│   💻 桌面工具                           │
│   ┌──────┐ ┌──────┐ ┌──────┐          │
│   │App 1 │ │App 2 │ │App 3 │  →更多    │
│   └──────┘ └──────┘ └──────┘          │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│   ✨ 新发现                             │
│   (最近7天新上架的优质项目)             │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│   📈 趋势榜                             │
│   (Star增长最快的项目)                 │
└────────────────────────────────────────┘
```

#### 4.5.2 推荐算法设计

```python
class RecommendationEngine:
    """推荐引擎"""
    
    async def get_hot_recommendations(self, limit=10):
        """热门推荐"""
        # 基于Stars数量的热门项目
        return await Repository.query.filter(
            Repository.is_active == True,
            Repository.has_releases == True,
            Repository.stars > 1000
        ).order_by(Repository.stars.desc()).limit(limit).all()
    
    async def get_trending_projects(self, days=7, limit=10):
        """趋势项目(Star增长快)"""
        # 计算最近N天的Star增长
        # 需要定期记录Stars快照
        pass
    
    async def get_new_discoveries(self, days=7, limit=10):
        """新发现(最近上架)"""
        return await Repository.query.filter(
            Repository.created_at >= now() - timedelta(days=days),
            Repository.has_releases == True,
            Repository.stars > 50
        ).order_by(Repository.created_at.desc()).limit(limit).all()
    
    async def get_category_recommendations(self, category, limit=10):
        """分类推荐"""
        return await Repository.query.filter(
            Repository.category == category,
            Repository.is_active == True,
            Repository.has_releases == True
        ).order_by(Repository.stars.desc()).limit(limit).all()
    
    async def get_user_personalized(self, user_id, limit=10):
        """个性化推荐(基于用户收藏)"""
        # 获取用户收藏的项目
        favorites = await UserFavorite.query.filter(
            UserFavorite.user_id == user_id
        ).all()
        
        # 提取用户偏好的分类、语言
        preferred_categories = Counter([f.repo.category for f in favorites])
        preferred_languages = Counter([f.repo.language for f in favorites])
        
        # 推荐相似项目
        recommendations = await Repository.query.filter(
            Repository.category.in_(preferred_categories.keys()),
            Repository.language.in_(preferred_languages.keys())
        ).order_by(Repository.stars.desc()).limit(limit).all()
        
        return recommendations
```

---

## 📡 五、API 接口设计

### 5.1 RESTful API 规范

```
基础路径: /api/v1

通用响应格式:
{
    "code": 200,              // 状态码
    "message": "success",     // 消息
    "data": {},              // 数据
    "timestamp": 1234567890  // 时间戳
}

错误响应格式:
{
    "code": 400,
    "message": "参数错误",
    "error": "phone字段缺失",
    "timestamp": 1234567890
}
```

### 5.2 核心接口列表

#### 5.2.1 用户认证接口

```
# 发送验证码
POST /api/v1/auth/send-code
Request:
{
    "phone": "13800138000",
    "type": "register"  // register | login | reset_password
}

# 注册
POST /api/v1/auth/register
Request:
{
    "phone": "13800138000",
    "code": "123456",
    "password": "abc123",
    "nickname": "用户昵称"  // 可选
}

# 登录
POST /api/v1/auth/login
Request:
{
    "phone": "13800138000",
    "password": "abc123"  // 或 "code": "123456"
}
Response:
{
    "code": 200,
    "data": {
        "token": "xxx",
        "user": {
            "id": 1,
            "phone": "13800138000",
            "nickname": "用户昵称",
            "avatar_url": "https://..."
        },
        "expires_at": "2026-02-05T00:00:00Z"
    }
}

# 退出登录
POST /api/v1/auth/logout
Headers: Authorization: Bearer {token}

# 刷新token
POST /api/v1/auth/refresh
Headers: Authorization: Bearer {token}
```

#### 5.2.2 项目查询接口

```
# 搜索项目
GET /api/v1/repositories/search
Query:
- q: 搜索关键词
- category: 分类
- language: 语言
- sort: 排序(stars/updated)
- page: 页码
- per_page: 每页数量

# 获取项目详情
GET /api/v1/repositories/:owner/:repo
Response:
{
    "code": 200,
    "data": {
        "id": 1,
        "full_name": "owner/repo",
        "name": "应用名称",
        "description": "描述",
        "stars": 1000,
        "language": "Kotlin",
        "topics": ["android"],
        "category": "android",
        "latest_release": {
            "tag_name": "v1.0.0",
            "published_at": "2026-01-29",
            "body": "更新日志..."
        },
        "readme": "README内容...",
        "is_favorited": false  // 是否已收藏(需登录)
    }
}

# 获取项目的所有Release
GET /api/v1/repositories/:owner/:repo/releases
Query:
- page: 页码
- per_page: 每页数量

# 获取项目的下载文件
GET /api/v1/releases/:release_id/assets
Response:
{
    "code": 200,
    "data": [
        {
            "id": 1,
            "name": "app-release.apk",
            "size": 45000000,
            "platform": "android",
            "file_type": "apk",
            "download_url": "https://github.com/...",
            "download_count": 1000
        }
    ]
}
```

#### 5.2.3 发现推荐接口

```
# 获取首页推荐
GET /api/v1/discover/home
Response:
{
    "code": 200,
    "data": {
        "banner": [...],           // 顶部Banner
        "hot": [...],              // 热门推荐
        "android": [...],          // Android应用
        "desktop": [...],          // 桌面工具
        "trending": [...],         // 趋势榜
        "new": [...]               // 新发现
    }
}

# 获取分类推荐
GET /api/v1/discover/category/:category
Query:
- page: 页码
- per_page: 每页数量

# 获取趋势榜
GET /api/v1/discover/trending
Query:
- period: 时间范围(daily/weekly/monthly)
```

#### 5.2.4 用户收藏接口

```
# 收藏项目
POST /api/v1/favorites
Headers: Authorization: Bearer {token}
Request:
{
    "repo_id": 1,
    "note": "备注"  // 可选
}

# 取消收藏
DELETE /api/v1/favorites/:repo_id
Headers: Authorization: Bearer {token}

# 获取收藏列表
GET /api/v1/favorites
Headers: Authorization: Bearer {token}
Query:
- page: 页码
- per_page: 每页数量

# 检查是否已收藏
GET /api/v1/favorites/check/:repo_id
Headers: Authorization: Bearer {token}
```

#### 5.2.5 AI助手接口

```
# 发送消息
POST /api/v1/ai/chat
Headers: Authorization: Bearer {token}  // 可选,游客有限制
Request:
{
    "message": "我想找一个安卓音乐播放器",
    "context": {
        "current_page": "search",
        "current_category": "android"
    }
}
Response:
{
    "code": 200,
    "data": {
        "reply": "AI回复内容...",
        "recommendations": [  // 推荐的项目(可选)
            {
                "repo_id": 1,
                "full_name": "owner/repo",
                "reason": "推荐理由"
            }
        ],
        "remaining_quota": 4  // 游客剩余对话次数
    }
}

# 获取对话历史
GET /api/v1/ai/history
Headers: Authorization: Bearer {token}
Query:
- page: 页码
- per_page: 每页数量
```

---

## 🚀 六、开发路线图

### 6.1 第一阶段: 核心功能开发 (2-3周)

**Week 1: 基础架构搭建**
```
Day 1-2: 
- ✅ 项目初始化
- ✅ 数据库设计和创建
- ✅ Redis配置
- ✅ 基础框架搭建(FastAPI)

Day 3-4:
- ✅ GitHub API封装
- ✅ 定时同步任务开发
- ✅ 数据同步逻辑实现

Day 5-7:
- ✅ 用户认证模块
- ✅ 短信服务集成
- ✅ JWT Token生成和验证
```

**Week 2: 核心业务功能**
```
Day 1-3:
- ✅ 项目搜索接口
- ✅ 项目详情接口
- ✅ Release信息接口
- ✅ 缓存策略实现

Day 4-5:
- ✅ 收藏功能开发
- ✅ 搜索历史记录

Day 6-7:
- ✅ Kimi AI集成
- ✅ AI助手接口开发
- ✅ 对话上下文管理
```

**Week 3: 前端开发**
```
Day 1-2:
- ✅ 首页布局
- ✅ 搜索页面
- ✅ 项目详情页

Day 3-4:
- ✅ 用户登录/注册页面
- ✅ 个人中心
- ✅ 收藏列表

Day 5-7:
- ✅ AI助手UI
- ✅ 响应式适配
- ✅ 交互优化
```

### 6.2 第二阶段: 发现推荐功能 (1-2周)

```
Week 4:
- ✅ 推荐算法开发
- ✅ 发现页面前端
- ✅ 趋势榜单计算
- ✅ 编辑推荐管理后台

Week 5:
- ✅ 个性化推荐
- ✅ Banner轮播管理
- ✅ 分类页面优化
```

### 6.3 第三阶段: 优化与测试 (1周)

```
Week 6:
- ✅ 性能优化
- ✅ 缓存策略调优
- ✅ API性能测试
- ✅ 前端加载优化

Week 7:
- ✅ 功能测试
- ✅ 用户体验测试
- ✅ 安全测试
- ✅ Bug修复
```

### 6.4 第四阶段: 上线部署 (3-5天)

```
- ✅ 服务器配置
- ✅ 数据库迁移
- ✅ Nginx配置
- ✅ HTTPS证书
- ✅ 域名解析
- ✅ 监控告警配置
- ✅ 灰度发布
- ✅ 正式上线
```

---

## 📊 七、性能与优化

### 7.1 性能指标目标

```
响应时间:
- 首页加载: < 1秒
- 搜索响应: < 500ms
- 项目详情: < 800ms
- AI对话响应: < 3秒

并发能力:
- 支持 1000+ QPS
- 支持 10000+ 在线用户

可用性:
- 服务可用性: 99.9%
- 数据持久化: 99.99%
```

### 7.2 缓存优化策略

```
多级缓存架构:

L1: 应用内存缓存
- 热点数据(前100个热门项目)
- 配置信息
- 用户会话

L2: Redis缓存
- 搜索结果
- 项目详情
- Release列表
- API配额

L3: PostgreSQL
- 全量数据
- 持久化存储

CDN缓存:
- 静态资源(JS/CSS/图片)
- 项目头像
- Banner图片
```

### 7.3 数据库优化

```
索引优化:
- 为高频查询字段添加索引
- 复合索引优化
- 定期分析查询性能

查询优化:
- 避免N+1查询
- 使用连接查询代替子查询
- 分页查询优化

连接池:
- 最小连接数: 10
- 最大连接数: 50
- 连接超时: 30秒
```

### 7.4 API限流策略

```
限流规则:

游客用户:
- 搜索: 20次/小时
- API调用: 100次/小时
- AI对话: 5次/天

注册用户:
- 搜索: 无限制
- API调用: 1000次/小时
- AI对话: 50次/天

实现方式:
- Redis + Token Bucket算法
- 按IP + 用户ID限流
- 超限后返回 429 状态码
```

---

## 🔒 八、安全设计

### 8.1 认证安全

```
密码存储:
- 使用 bcrypt 哈希
- 加盐(Salt)处理
- 不存储明文密码

Token安全:
- JWT Token
- 有效期: 7天
- 支持刷新机制
- 存储在 HttpOnly Cookie

会话管理:
- 单设备登录踢出机制
- 异地登录提醒
- 定期刷新Token
```

### 8.2 接口安全

```
防护措施:

HTTPS:
- 强制使用HTTPS
- TLS 1.2+

CORS:
- 限制允许的域名
- 验证 Origin 头

XSS防护:
- 输入过滤
- 输出转义
- CSP策略

SQL注入防护:
- ORM参数化查询
- 输入验证

CSRF防护:
- CSRF Token
- SameSite Cookie
```

### 8.3 数据安全

```
敏感数据:
- 手机号脱敏显示(138****8000)
- GitHub Token加密存储
- 用户密码不可逆加密

数据备份:
- 每日全量备份
- 实时增量备份
- 异地容灾备份

访问控制:
- 数据库访问白名单
- API访问频率限制
- 敏感操作审计日志
```

---

## 📈 九、监控与运维

### 9.1 监控指标

```
系统监控:
- CPU使用率
- 内存使用率
- 磁盘IO
- 网络流量

应用监控:
- API响应时间
- 错误率
- QPS
- 慢查询

业务监控:
- 用户注册数
- 活跃用户数
- 搜索次数
- 下载次数
- AI对话次数
```

### 9.2 告警策略

```
告警级别:

P0 - 紧急:
- 服务不可用
- 数据库连接失败
- Redis宕机
- 发送短信/电话

P1 - 重要:
- API错误率 > 5%
- 响应时间 > 3秒
- CPU使用率 > 80%
- 发送短信

P2 - 一般:
- 慢查询增多
- 缓存命中率下降
- 发送邮件

告警渠道:
- 短信
- 邮件
- 钉钉/企业微信
- 电话(紧急情况)
```

### 9.3 日志管理

```
日志分类:

访问日志:
- 记录所有API请求
- 包含IP、User-Agent、响应时间

错误日志:
- 记录所有异常
- 包含堆栈信息
- 便于问题排查

业务日志:
- 用户行为日志
- 同步任务日志
- AI对话日志

日志存储:
- 本地文件存储
- 定期归档到OSS
- 保留30天
```

---

## 📝 十、总结与下一步

### 10.1 本期目标

✅ **核心功能完整**
- 用户注册登录(手机号)
- 项目搜索浏览
- 详情展示和下载
- 收藏功能
- AI智能助手
- 发现推荐页面

✅ **性能稳定**
- 多级缓存架构
- 定时同步机制
- API限流保护

✅ **用户体验优化**
- GitHub风格UI
- 响应式设计
- 通俗易懂的语言

### 10.2 后续规划

**短期(1-2个月):**
- 优化推荐算法
- 完善AI助手能力
- 增加更多应用分类
- 移动端适配优化

**中期(3-6个月):**
- 开发独立的移动App
- 增加应用更新提醒
- 建立用户反馈机制
- 数据分析看板

**长期(6-12个月):**
- 支持多语言
- 国际化版本
- 引入更多AI能力
- 探索商业化模式

---

## 📞 十一、附录

### 11.1 技术选型理由

| 技术 | 理由 |
|------|------|
| FastAPI | 高性能、异步、自动文档生成 |
| PostgreSQL | 成熟稳定、支持JSON、全文搜索 |
| Redis | 高性能缓存、支持多种数据结构 |
| Celery | 分布式任务队列、支持定时任务 |
| Kimi API | 中文友好、响应快、成本合理 |

### 11.2 开发规范

```
代码规范:
- 遵循 PEP 8
- 函数/类添加文档注释
- 使用类型提示

Git规范:
- 分支策略: main/dev/feature
- Commit格式: feat/fix/docs/style/refactor
- 代码审查后合并

测试规范:
- 单元测试覆盖率 > 80%
- 集成测试覆盖核心功能
- 上线前完整回归测试
```

### 11.3 部署环境

```
生产环境:
- 操作系统: Ubuntu 22.04 LTS
- Python: 3.11+
- PostgreSQL: 15+
- Redis: 7.0+
- Nginx: 1.24+

服务器配置:
- 最低: 2核4G 40G硬盘
- 推荐: 4核8G 100G硬盘
- 带宽: 5Mbps+
```

---

**文档版本**: v1.0  
**最后更新**: 2026-01-29  
**维护人员**: 开发团队