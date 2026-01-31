# GitHub Releases Store - 开发计划

## 当前状态分析

### 已实现功能
- [x] 后端基础架构 (FastAPI, SQLAlchemy, Pydantic)
- [x] 数据库模型 (User, Repository, Release, ReleaseAsset, UserFavorite, Recommendation, SystemConfig)
- [x] CRUD 操作
- [x] GitHub API 客户端
- [x] Kimi AI 客户端
- [x] Celery 同步任务框架
- [x] API 路由结构
- [x] 前端 Vue 3 + Tailwind CSS 框架
- [x] 页面路由 (Home, Search, Detail, Login, Register, Profile, Discovery)

### 待解决问题
1. **数据库无数据** - 没有执行数据同步
2. **缺少手动同步脚本** - 需要不依赖 Celery 的同步方式
3. **Release/Asset 同步未实现** - 只同步了仓库基本信息
4. **搜索 API 不完整** - repositories 端点需要完善
5. **前端 API 服务未配置** - 需要创建统一的 API 服务层
6. **前端组件未完善** - 组件功能不完整

---

## 开发任务列表

### Phase 1: 数据同步与获取 (优先级: P0)

#### 1.1 创建手动同步脚本
- 创建 `scripts/sync_data.py` 脚本
- 支持命令行参数控制同步范围
- 同步仓库基本信息
- 同步 Releases 和 Assets

#### 1.2 完善 Release 同步
- 在 tasks.py 中添加 release 同步逻辑
- 同步 release assets (下载文件)
- 解析平台类型 (android/windows/macos/linux)

#### 1.3 初始数据填充
- 预设一些热门开源项目
- 执行首次数据同步
- 验证数据正确性

### Phase 2: 后端 API 完善 (优先级: P0)

#### 2.1 搜索 API
- 实现 `/api/v1/repositories/search` 端点
- 支持关键词搜索
- 支持分类、语言过滤
- 支持分页和排序

#### 2.2 仓库详情 API
- 完善 `/api/v1/repositories/{owner}/{repo}` 端点
- 返回 releases 列表
- 返回 assets 信息
- 返回 README 内容

#### 2.3 Discover API 完善
- 实现分类推荐
- 实现趋势榜单
- 添加 Banner 数据

### Phase 3: 前端完善 (优先级: P1)

#### 3.1 API 服务层
- 创建 `src/services/api.js` 统一封装
- 配置 axios 拦截器
- 处理认证 token
- 统一错误处理

#### 3.2 首页 (HomePage)
- 显示热门推荐
- 显示分类入口
- 集成 AI 聊天组件

#### 3.3 发现页 (DiscoveryPage)
- 完善数据展示
- 添加加载状态
- 添加错误处理

#### 3.4 搜索页 (SearchPage)
- 实现搜索表单
- 显示搜索结果
- 支持筛选和排序

#### 3.5 详情页 (DetailPage)
- 显示仓库信息
- 显示 Release 列表
- 显示下载按钮
- 收藏功能

#### 3.6 用户相关页面
- 完善登录/注册表单
- 个人中心页面
- 收藏列表

### Phase 4: 功能增强 (优先级: P2)

#### 4.1 AI 助手
- 完善对话界面
- 实现上下文管理
- 添加推荐功能

#### 4.2 用户体验优化
- 加载状态指示
- 错误提示
- 响应式适配

---

## 执行顺序

```
1. [Phase 1.1] 创建手动同步脚本
2. [Phase 1.2] 完善 Release 同步
3. [Phase 1.3] 执行数据同步
4. [Phase 2.1] 搜索 API
5. [Phase 2.2] 仓库详情 API
6. [Phase 3.1] 前端 API 服务层
7. [Phase 3.2] 首页完善
8. [Phase 3.3] 发现页完善
9. [Phase 3.4] 搜索页实现
10. [Phase 3.5] 详情页实现
11. [Phase 3.6] 用户页面完善
12. [Phase 4.1] AI 助手增强
13. [Phase 4.2] 用户体验优化
```

---

## 验收标准

1. 数据库中有至少 50 个仓库数据
2. 首页能正确显示热门推荐
3. 搜索功能可用
4. 仓库详情页能显示 Release 和下载链接
5. 用户可以登录并收藏项目
6. AI 助手可以正常对话
