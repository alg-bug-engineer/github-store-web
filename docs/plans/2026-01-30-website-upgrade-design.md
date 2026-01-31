# GitHub Store Web 网站升级设计文档

> 创建日期: 2026-01-30
> 状态: 待审批

---

## 1. 项目概述

### 1.1 升级目标

将当前的 "GitHub 代码浏览器" 风格转变为 "应用商店" 风格，让用户能够：
- 快速找到可下载的软件应用
- 一眼识别支持的平台（Windows/Mac/Linux/Android）
- 直接在卡片上看到版本信息和下载按钮
- 通过平台和分类进行精确筛选

### 1.2 核心原则

1. **下载优先**：用户来这里是为了下载软件，不是浏览代码
2. **平台明确**：用户需要快速判断软件是否适用于自己的系统
3. **版本可见**：展示最新版本和更新时间，证明软件仍在维护
4. **视觉现代**：提供深色主题选项，符合现代应用商店审美

---

## 2. 主题系统设计

### 2.1 双主题支持

提供手动切换的亮色/深色主题，用户偏好保存至 localStorage。

### 2.2 深色主题配色方案

参考附件图片的紫绿配色风格：

```css
/* 背景层级 */
--bg-primary: #0d0d0f;      /* 最深背景 */
--bg-secondary: #1a1a1d;    /* 卡片背景 */
--bg-tertiary: #252529;     /* 悬停状态、输入框 */

/* 强调色 */
--accent-primary: #8b5cf6;   /* 紫色 - 主按钮、激活状态 */
--accent-secondary: #22c55e; /* 绿色 - 成功、下载按钮 */
--accent-tertiary: #3b82f6;  /* 蓝色 - 链接、信息标签 */

/* 文字颜色 */
--text-primary: #f4f4f5;     /* 标题、重要文字 */
--text-secondary: #a1a1aa;   /* 描述、次要文字 */
--text-tertiary: #71717a;    /* 时间戳、元数据 */

/* 边框 */
--border-default: #27272a;   /* 默认边框 */
--border-hover: #3f3f46;     /* 悬停边框 */

/* 标签颜色 */
--label-purple: #8b5cf6;
--label-green: #22c55e;
--label-blue: #3b82f6;
--label-orange: #f97316;
--label-gray: #71717a;
```

### 2.3 亮色主题配色方案

保留当前 GitHub 风格的亮色主题：

```css
/* 背景层级 */
--bg-primary: #ffffff;
--bg-secondary: #f6f8fa;
--bg-tertiary: #f0f0f0;

/* 强调色 */
--accent-primary: #8b5cf6;
--accent-secondary: #22c55e;
--accent-tertiary: #0969da;

/* 文字颜色 */
--text-primary: #1f2328;
--text-secondary: #656d76;
--text-tertiary: #8b949e;

/* 边框 */
--border-default: #d0d7de;
--border-hover: #bbc0c5;
```

### 2.4 主题切换实现

```javascript
// 切换逻辑
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

// 初始化（在 <head> 中执行，避免闪烁）
const saved = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', saved);
```

### 2.5 主题切换按钮

- 位置：Header 导航栏右侧
- 图标：亮色模式显示 🌙（月亮），深色模式显示 ☀️（太阳）
- 交互：点击切换，带 200ms 过渡动画

---

## 3. 导航与布局设计

### 3.1 整体布局结构

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER                                                           │
│ [Logo] GitHub Store    [Downloadable Apps | All Repos]   [🌙]    │
├──────────────────────────────────────────────────────────────────┤
│ HERO SECTION                                                     │
│ 标题 + 副标题                                                     │
│ [🔍 搜索框...]                                                   │
│ [统计数据卡片: Repositories | Releases | Downloads | Categories] │
├──────────────────────────────────────────────────────────────────┤
│ FILTER BAR                                                       │
│ [Android] [Windows] [Mac] [Linux] [All] | [Category▾] [Lang▾]   │
├──────────────────────────────────────────────────────────────────┤
│ CONTENT GRID                                                     │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                             │
│ │ App Card│ │ App Card│ │ App Card│                             │
│ └─────────┘ └─────────┘ └─────────┘                             │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐                             │
│ │ App Card│ │ App Card│ │ App Card│                             │
│ └─────────┘ └─────────┘ └─────────┘                             │
├──────────────────────────────────────────────────────────────────┤
│ FOOTER                                                           │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 视图模式切换

**两种视图模式：**

| 模式 | 说明 | 数据筛选 |
|------|------|----------|
| Downloadable Apps | 默认视图，仅显示有 Release 二进制文件的仓库 | `has_releases = true` |
| All Repositories | 显示所有仓库，包括纯代码库 | 无筛选 |

**实现方式：**
- Header 中使用 Tab 样式切换
- 默认加载 "Downloadable Apps" 视图
- 切换时 URL 更新：`/?view=apps` / `/?view=all`
- 用户选择保存至 localStorage

### 3.3 平台筛选 Pills

**主要平台（一级筛选）：**

```
[Android] [Windows] [Mac] [Linux] [All Platforms]
```

- 单选模式：点击一个平台，取消其他平台选中
- "All Platforms" 为重置按钮
- 激活状态使用 `--accent-primary` 紫色背景

**平台图标：**
- Android: 🤖 或 Android logo SVG
- Windows: 🪟 或 Windows logo SVG
- Mac: 🍎 或 Apple logo SVG
- Linux: 🐧 或 Tux logo SVG

### 3.4 二级筛选下拉菜单

**分类下拉 (Category)：**
- All Categories（默认）
- Productivity / 生产力工具
- Developer Tools / 开发工具
- Media & Entertainment / 媒体娱乐
- Utilities / 实用工具
- Games / 游戏
- Security / 安全工具
- Education / 教育学习

**语言下拉 (Language)：**
- All Languages（默认）
- Python, JavaScript, TypeScript, Go, Rust, Java, C++, C#, Swift, Kotlin 等

**排序下拉 (Sort)：**
- Most Stars（默认）
- Recently Updated
- Newest Added
- Most Downloads

### 3.5 筛选组合逻辑

所有筛选条件为 AND 关系：

```
view=apps AND platform=mac AND category=productivity AND language=python
```

URL 同步更新，支持分享筛选结果链接：
```
https://example.com/?view=apps&platform=mac&category=productivity
```

---

## 4. 应用卡片设计

### 4.1 卡片布局

```
┌─────────────────────────────────────────────────────────┐
│  [Avatar]  App Name                         v2.3.0     │
│            owner/repo                                   │
│                                                         │
│  Short description text that can span up to two        │
│  lines with ellipsis overflow...                       │
│                                                         │
│  [tag1] [tag2] [tag3] +2                               │
│                                                         │
│  🪟 🍎 🐧                           [⬇ Download ▾]     │
│  ●Python | ⭐ 12.5k | 🔀 1.2k | Updated 2 days ago    │
└─────────────────────────────────────────────────────────┘
```

### 4.2 卡片元素详解

| 元素 | 说明 | 样式 |
|------|------|------|
| Avatar | 仓库所有者头像 | 40x40px, 圆角 |
| App Name | 仓库名称 | 16px, font-weight: 600 |
| owner/repo | 完整路径 | 12px, text-secondary |
| Version Badge | 最新版本号 | 胶囊标签，绿色背景 |
| Description | 仓库描述 | 14px, 2行截断，text-secondary |
| Tags | 前3个 topics | 小标签，点击可筛选 |
| Platform Icons | 支持的平台图标 | 悬停显示平台名称 tooltip |
| Download Button | 下载按钮 | 绿色，带下拉选择不同资源 |
| Language | 编程语言 | 带颜色圆点 |
| Stars | 星标数 | 格式化显示 (1.2k, 12.5k) |
| Forks | Fork 数 | 格式化显示 |
| Updated | 更新时间 | 相对时间 (2 days ago) |

### 4.3 版本徽章设计

```html
<span class="version-badge">v2.3.0</span>
```

```css
.version-badge {
  background: var(--accent-secondary);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
```

### 4.4 平台图标显示逻辑

根据 Release Assets 的文件名/类型自动检测：

| 文件特征 | 平台 |
|----------|------|
| `.exe`, `.msi`, `win`, `windows` | Windows 🪟 |
| `.dmg`, `.pkg`, `mac`, `darwin`, `macos` | Mac 🍎 |
| `.deb`, `.rpm`, `.AppImage`, `linux` | Linux 🐧 |
| `.apk`, `android` | Android 🤖 |

**显示规则：**
- 卡片上始终显示检测到的平台图标
- 悬停时显示 tooltip：`Supports: Windows, Mac, Linux`
- 如果没有检测到平台，显示通用下载图标

### 4.5 下载按钮交互

**单一资源：**
```
[⬇ Download]  // 直接下载
```

**多个资源：**
```
[⬇ Download ▾]  // 点击展开下拉菜单
  ├─ Windows (.exe) - 45.2 MB
  ├─ Mac (.dmg) - 52.1 MB
  └─ Linux (.AppImage) - 48.7 MB
```

**无 Release：**
```
[View Source]  // 跳转到 GitHub 仓库
```

### 4.6 卡片悬停效果

```css
.app-card {
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}

.app-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: var(--accent-primary);
}

/* 深色模式下的悬停 */
[data-theme="dark"] .app-card:hover {
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2);
}
```

---

## 5. 统计数据展示

### 5.1 统计卡片布局

```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│     📦      │ │     🏷️      │ │     ⬇️      │ │     📂      │
│    156      │ │    892      │ │   45.2k     │ │     12      │
│ Repositories│ │  Releases   │ │  Downloads  │ │ Categories  │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### 5.2 实时数据 API

新增后端接口获取统计数据：

```python
# GET /api/v1/stats/overview
{
  "repositories_count": 156,
  "releases_count": 892,
  "total_downloads": 45234,
  "categories_count": 12,
  "last_updated": "2026-01-30T10:30:00Z"
}
```

### 5.3 数字动画效果

使用 count-up 动画，数字从 0 增长到目标值：

```javascript
function animateCount(element, target, duration = 1500) {
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeOut = 1 - Math.pow(1 - progress, 3); // easeOutCubic
    const current = Math.floor(start + (target - start) * easeOut);

    element.textContent = formatNumber(current);

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num.toString();
}
```

### 5.4 触发时机

- 使用 Intersection Observer 检测统计区域进入视口
- 首次进入视口时触发动画
- 动画只播放一次，不重复

---

## 6. 数据模型更新

### 6.1 Repository 模型扩展

```python
class Repository(Base):
    # 现有字段...

    # 新增字段
    detected_platforms = Column(ARRAY(String), default=[])  # ['windows', 'mac', 'linux']
    primary_category = Column(String, nullable=True)  # 'productivity', 'developer_tools', etc.
    total_downloads = Column(Integer, default=0)
    latest_version = Column(String, nullable=True)  # 'v2.3.0'
    latest_release_date = Column(DateTime, nullable=True)
```

### 6.2 平台检测服务

```python
def detect_platforms_from_assets(assets: List[ReleaseAsset]) -> List[str]:
    platforms = set()

    for asset in assets:
        name = asset.name.lower()

        if any(x in name for x in ['.exe', '.msi', 'win', 'windows']):
            platforms.add('windows')
        if any(x in name for x in ['.dmg', '.pkg', 'mac', 'darwin', 'macos']):
            platforms.add('mac')
        if any(x in name for x in ['.deb', '.rpm', '.appimage', 'linux']):
            platforms.add('linux')
        if any(x in name for x in ['.apk', 'android']):
            platforms.add('android')

    return list(platforms)
```

### 6.3 分类映射

```python
CATEGORY_KEYWORDS = {
    'productivity': ['productivity', 'office', 'notes', 'todo', 'calendar'],
    'developer_tools': ['developer', 'ide', 'editor', 'terminal', 'git', 'code'],
    'media': ['video', 'audio', 'music', 'player', 'streaming', 'media'],
    'utilities': ['utility', 'tool', 'system', 'monitor', 'cleaner'],
    'games': ['game', 'gaming', 'emulator'],
    'security': ['security', 'password', 'vpn', 'encryption', 'privacy'],
    'education': ['education', 'learning', 'tutorial', 'course'],
}

def detect_category(repo: Repository) -> str:
    text = f"{repo.name} {repo.description} {' '.join(repo.topics or [])}".lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category

    return 'other'
```

---

## 7. API 接口更新

### 7.1 统计概览接口

```
GET /api/v1/stats/overview

Response:
{
  "repositories_count": 156,
  "releases_count": 892,
  "total_downloads": 45234,
  "categories_count": 12
}
```

### 7.2 仓库列表接口更新

```
GET /api/v1/repositories/

Query Parameters:
- view: 'apps' | 'all' (default: 'apps')
- platform: 'android' | 'windows' | 'mac' | 'linux' | null
- category: string | null
- language: string | null
- q: string (搜索关键词)
- sort: 'stars' | 'updated' | 'created' | 'downloads' (default: 'stars')
- page: int (default: 1)
- per_page: int (default: 20)

Response:
{
  "items": [
    {
      "id": 1,
      "name": "app-name",
      "full_name": "owner/app-name",
      "description": "...",
      "stars_count": 12500,
      "forks_count": 1200,
      "language": "Python",
      "topics": ["tag1", "tag2"],
      "latest_version": "v2.3.0",
      "latest_release_date": "2026-01-28T10:00:00Z",
      "detected_platforms": ["windows", "mac", "linux"],
      "primary_category": "productivity",
      "has_releases": true,
      "owner_avatar_url": "https://..."
    }
  ],
  "total": 156,
  "page": 1,
  "per_page": 20
}
```

### 7.3 分类列表接口

```
GET /api/v1/categories/

Response:
{
  "categories": [
    {"id": "productivity", "name": "Productivity", "count": 23},
    {"id": "developer_tools", "name": "Developer Tools", "count": 45},
    ...
  ]
}
```

---

## 8. 前端组件更新

### 8.1 新增组件

| 组件 | 用途 |
|------|------|
| `ThemeToggle.vue` | 主题切换按钮 |
| `ViewModeSwitch.vue` | Apps/All 视图切换 |
| `PlatformFilter.vue` | 平台筛选 pills |
| `FilterDropdown.vue` | 通用下拉筛选器 |
| `AppCard.vue` | 新版应用卡片（替代 RepoCard） |
| `VersionBadge.vue` | 版本号徽章 |
| `PlatformIcons.vue` | 平台图标组 |
| `DownloadButton.vue` | 下载按钮（带下拉） |
| `StatsCounter.vue` | 动画统计数字 |
| `StatsOverview.vue` | 统计概览区域 |

### 8.2 修改组件

| 组件 | 修改内容 |
|------|----------|
| `App.vue` | 添加主题属性、主题切换按钮 |
| `Header.vue` | 添加视图模式切换、主题切换 |
| `HomePage.vue` | 使用新统计组件、新筛选栏 |
| `SearchPage.vue` | 使用新筛选系统 |
| `DiscoveryPage.vue` | 适配新卡片组件 |

### 8.3 样式文件更新

```
frontend/src/assets/
├── styles/
│   ├── variables.css      # CSS 变量定义（新增）
│   ├── theme-light.css    # 亮色主题变量
│   ├── theme-dark.css     # 深色主题变量
│   ├── components.css     # 组件样式
│   └── github-theme.css   # 保留，做迁移兼容
```

---

## 9. 实施计划

### Phase 1: 基础设施（预计 2-3 天）

- [ ] 1.1 创建 CSS 变量系统和主题文件
- [ ] 1.2 实现 ThemeToggle 组件
- [ ] 1.3 更新 App.vue 支持主题切换
- [ ] 1.4 测试主题切换功能

### Phase 2: 后端更新（预计 2 天）

- [ ] 2.1 扩展 Repository 模型（新增字段）
- [ ] 2.2 实现平台检测服务
- [ ] 2.3 实现分类检测服务
- [ ] 2.4 创建统计概览 API
- [ ] 2.5 更新仓库列表 API（支持新筛选参数）
- [ ] 2.6 创建分类列表 API
- [ ] 2.7 编写数据迁移脚本

### Phase 3: 筛选系统（预计 2 天）

- [ ] 3.1 实现 ViewModeSwitch 组件
- [ ] 3.2 实现 PlatformFilter 组件
- [ ] 3.3 实现 FilterDropdown 组件
- [ ] 3.4 更新 Header 布局
- [ ] 3.5 实现 URL 状态同步

### Phase 4: 卡片重构（预计 2-3 天）

- [ ] 4.1 实现 VersionBadge 组件
- [ ] 4.2 实现 PlatformIcons 组件
- [ ] 4.3 实现 DownloadButton 组件
- [ ] 4.4 实现 AppCard 组件
- [ ] 4.5 替换现有 RepoCard 使用

### Phase 5: 统计与动画（预计 1 天）

- [ ] 5.1 实现 StatsCounter 组件（带动画）
- [ ] 5.2 实现 StatsOverview 组件
- [ ] 5.3 更新 HomePage 使用新统计组件

### Phase 6: 集成测试与优化（预计 1-2 天）

- [ ] 6.1 全站功能测试
- [ ] 6.2 深色/亮色主题视觉检查
- [ ] 6.3 无障碍对比度检查
- [ ] 6.4 性能优化
- [ ] 6.5 响应式设计验证

---

## 10. 技术注意事项

### 10.1 主题切换防闪烁

在 `index.html` 的 `<head>` 中添加内联脚本，在 CSS 加载前设置主题：

```html
<script>
  (function() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
```

### 10.2 CSS 变量兼容性

使用 CSS 变量实现主题，确保所有颜色值都通过变量引用：

```css
/* 避免硬编码颜色 */
.card {
  background: var(--bg-secondary);  /* 正确 */
  background: #1a1a1d;              /* 避免 */
}
```

### 10.3 深色模式无障碍

确保对比度符合 WCAG AA 标准（4.5:1）：

- 正文文字与背景对比度 ≥ 4.5:1
- 大标题与背景对比度 ≥ 3:1
- 使用工具验证：Chrome DevTools 或 axe-core

### 10.4 平台检测准确性

平台检测基于文件名启发式规则，可能存在误判。建议：

1. 提供管理后台手动修正功能
2. 记录检测日志便于优化规则
3. 对于无法检测的情况，显示通用图标

### 10.5 数据迁移

新增字段需要数据回填：

```python
# 迁移脚本
def backfill_repository_metadata():
    repos = session.query(Repository).all()
    for repo in repos:
        # 获取最新 release
        latest_release = get_latest_release(repo.id)
        if latest_release:
            repo.latest_version = latest_release.tag_name
            repo.latest_release_date = latest_release.published_at

            # 检测平台
            assets = get_release_assets(latest_release.id)
            repo.detected_platforms = detect_platforms_from_assets(assets)

        # 检测分类
        repo.primary_category = detect_category(repo)

    session.commit()
```

---

## 11. 验收标准

### 功能验收

- [ ] 主题切换正常工作，刷新后保持选择
- [ ] "Downloadable Apps" 视图仅显示有 Release 的仓库
- [ ] 平台筛选正确过滤结果
- [ ] 二级分类筛选正确组合
- [ ] 卡片显示版本号、平台图标、下载按钮
- [ ] 下载按钮点击可下载文件
- [ ] 统计数字从 API 获取并有动画效果
- [ ] URL 同步筛选状态，可分享

### 视觉验收

- [ ] 深色主题配色符合设计稿
- [ ] 亮色主题保持 GitHub 风格
- [ ] 卡片悬停效果流畅
- [ ] 移动端响应式正常
- [ ] 无障碍对比度合格

### 性能验收

- [ ] 首屏加载时间 < 3s
- [ ] 筛选切换响应时间 < 500ms
- [ ] 无明显卡顿或闪烁

---

## 12. 附录

### A. 参考设计

- 参考图片：深色主题、紫绿配色、卡片网格布局
- 参考应用商店：App Store、Google Play、Steam

### B. 相关文档

- 现有 API 文档：`/docs/swagger`
- 数据库模型：`backend/app/models/`
- 前端组件：`frontend/src/components/`

---

**文档版本**: v1.0
**最后更新**: 2026-01-30
