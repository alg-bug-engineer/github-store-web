# AI 助手侧边栏设计方案

> 日期：2025-02-01
> 状态：已确认，待实施

## 概述

在左侧边栏底部添加 AI 助手入口，基于 RAG（检索增强生成）实现项目推荐功能。用户通过对话方式描述需求，AI 检索匹配的项目并返回推荐结果，结果中的项目支持点击跳转到详情页。

## 技术选型

| 维度 | 选择 | 理由 |
|------|------|------|
| 位置 | 左侧边栏底部 | 与现有导航一致，不遮挡主内容 |
| 检索方式 | PostgreSQL 文本搜索 | 简单高效，无需额外依赖 |
| AI 模型 | Kimi (Moonshot) | 复用现有配置，中文支持好 |
| 展开方式 | 侧边栏内向上展开 | 可边聊边浏览 |

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                          用户界面                                │
│  ┌──────────────┐  ┌─────────────────────────────────────────┐  │
│  │   侧边栏      │  │              主内容区                    │  │
│  │              │  │                                         │  │
│  │  Store       │  │                                         │  │
│  │  Collections │  │                                         │  │
│  │  Personal    │  │                                         │  │
│  │              │  │                                         │  │
│  │  ┌────────┐  │  │                                         │  │
│  │  │ AI 聊天 │  │  │                                         │  │
│  │  │ 面板    │  │  │                                         │  │
│  │  │(展开时) │  │  │                                         │  │
│  │  └────────┘  │  │                                         │  │
│  │  [🤖 AI]     │  │                                         │  │
│  └──────────────┘  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**数据流：**

```
用户输入 → 后端 API → 文本检索（PostgreSQL） → 构建 Prompt → Kimi API → 格式化响应 → 前端展示
```

## 后端 API 设计

### 端点：`POST /api/v1/ai/chat`

**请求体：**

```json
{
  "message": "我想找一个写小红书的工具",
  "conversation_id": "optional-uuid"
}
```

**响应体：**

```json
{
  "reply": "根据您的需求，我为您找到了以下工具：...",
  "projects": [
    {
      "id": 123,
      "name": "awesome-writing-tool",
      "full_name": "owner/awesome-writing-tool",
      "description": "...",
      "url": "/repo/owner/awesome-writing-tool"
    }
  ],
  "conversation_id": "uuid"
}
```

### 处理流程

```
1. 接收用户消息
      ↓
2. 关键词提取 + PostgreSQL 搜索
   - 搜索 name, description, topics 字段
   - 使用 ILIKE 模糊匹配
   - 返回 top 5 相关项目
      ↓
3. 构建 RAG Prompt
   - System: 你是项目推荐助手...
   - Context: 检索到的项目信息
   - User: 用户原始问题
      ↓
4. 调用 Kimi API 生成回复
      ↓
5. 返回结构化响应（文本 + 项目列表）
```

## 前端 UI 设计

### 收起状态

```
┌─────────────────┐
│  ...            │
│  Personal       │
│  ├─ Starred     │
│  └─ Settings    │
│                 │
│  ─────────────  │  ← 分隔线
│  🤖 AI Assistant│  ← 点击展开
└─────────────────┘
```

### 展开状态

```
┌─────────────────┐
│  Store          │  ← 导航被压缩
│  ─────────────  │
│ ┌─────────────┐ │
│ │ AI Assistant│ │  ← 标题 + 关闭按钮
│ ├─────────────┤ │
│ │ 👋 你好！    │ │
│ │             │ │
│ │ [用户消息]  │ │
│ │             │ │
│ │ [AI回复]    │ │
│ │ ┌─────────┐ │ │
│ │ │📦 项目1  │→│ │  ← 可点击跳转
│ │ │📦 项目2  │→│ │
│ │ └─────────┘ │ │
│ ├─────────────┤ │
│ │ [输入框] 📤 │ │
│ └─────────────┘ │
└─────────────────┘
```

### 交互规则

1. 点击 "AI Assistant" 入口 → 面板向上展开（高度约 400px）
2. 项目卡片点击 → `router.push('/repo/owner/name')`
3. 点击关闭/再次点击入口 → 面板收起
4. 聊天记录在当前会话内保持

## 检索逻辑

### SQL 查询

```sql
SELECT id, name, full_name, description, topics, stars, avatar_url
FROM repositories
WHERE is_active = true
  AND (
    name ILIKE '%关键词%'
    OR description ILIKE '%关键词%'
    OR EXISTS (SELECT 1 FROM unnest(topics) t WHERE t ILIKE '%关键词%')
  )
ORDER BY
  CASE WHEN name ILIKE '%关键词%' THEN 0 ELSE 1 END,
  stars DESC
LIMIT 5;
```

### 关键词提取

```python
def extract_keywords(message: str) -> list[str]:
    """
    从用户消息中提取搜索关键词
    使用简单分词 + 停用词过滤
    """
```

### 无结果处理

检索结果为空时，AI 回复："抱歉，暂时没有找到相关的项目。您可以尝试换个关键词，或者告诉我更具体的需求。"

## Prompt 设计

### System Prompt

```
你是 GitHub Store 的 AI 助手，帮助用户发现和推荐开源项目。

## 职责
1. 理解用户需求，推荐合适的项目
2. 用通俗易懂的语言介绍项目功能
3. 如果没有找到合适的项目，诚实告知

## 回复规则
- 语言简洁友好，控制在 100 字以内
- 推荐项目时，简要说明为什么适合用户需求
- 项目名称用 【项目名】 格式标注，方便前端识别
- 不要编造不存在的项目
```

### 带检索结果的 User Prompt

```
用户问题：{user_message}

我为你检索到以下相关项目：
{foreach project}
- 【{project.name}】: {project.description}
  Stars: {project.stars} | 分类: {project.category}
{/foreach}

请根据用户需求，从上述项目中推荐最合适的，并简要说明推荐理由。
```

### 无检索结果的 User Prompt

```
用户问题：{user_message}

抱歉，我没有找到与此相关的项目。请友好地告知用户，并建议他们：
1. 尝试更换关键词
2. 描述更具体的需求
```

## 文件变更清单

### 后端（backend/）

| 文件 | 操作 | 说明 |
|------|------|------|
| `app/api/v1/endpoints/ai.py` | 修改 | 新增 `/chat` 端点 |
| `app/services/ai_search.py` | 新建 | 检索服务（关键词提取 + 数据库搜索） |
| `app/schemas/ai.py` | 新建 | ChatRequest / ChatResponse 模型 |

### 前端（frontend/）

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/components/AISidebar.vue` | 新建 | 侧边栏 AI 聊天组件 |
| `src/App.vue` | 修改 | 集成 AISidebar 到侧边栏 |
| `src/services/api.js` | 修改 | 更新 aiAPI.chat 方法 |

### 可删除

| 文件 | 说明 |
|------|------|
| `src/components/AIChat.vue` | 旧的浮动聊天窗口（可选保留） |

## 实施顺序

1. 后端：新增检索服务 + chat API
2. 前端：创建 AISidebar 组件
3. 前端：集成到 App.vue 侧边栏
4. 测试：端到端验证
5. 清理：移除旧 AIChat 组件（可选）

## 后续优化（可选）

- 升级为 pgvector 向量检索
- 支持多轮对话上下文
- 添加常用问题快捷入口
- 支持语音输入
