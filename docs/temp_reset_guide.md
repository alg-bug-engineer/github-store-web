# 数据库变更总结与数据重置指南

## 1. 数据库变更总结 (Summary of Database Changes)

*   **没有新增的库表 (No New Tables):**
    *   本次开发没有新增任何数据库表。

*   **`Repository` 表新增字段 (New Fields in `Repository` Table):**
    *   在 `Repository` 表中增加了以下 5 个字段，以支持新的筛选和展示功能。您可以在 `backend/app/models/repository.py` 文件中查看这些变更。
        *   `detected_platforms`: (ARRAY of Strings) - 用于存储检测到的应用平台 (e.g., 'windows', 'mac')。
        *   `primary_category`: (String) - 用于存储检测到的应用主分类 (e.g., 'developer_tools')。
        *   `total_downloads`: (Integer) - 用于存储该仓库所有版本资源的总下载量。
        *   `latest_version`: (String) - 用于存储最新发布版本的版本号 (e.g., 'v2.3.0')。
        *   `latest_release_date`: (DateTime) - 用于存储最新发布版本的发布日期。

## 2. 如何重置数据 (How to Reset Data)

重置数据需要以下四个步骤，这将彻底清空并重新初始化您的数据库：

### Step 1: 删除所有数据表 (Drop All Tables)
我已为您创建了一个新脚本 `backend/scripts/reset_db.py` 来安全地执行此操作。

在 `backend` 目录下运行:
```bash
python scripts/reset_db.py
```
*该脚本会提示您确认，以防止意外删除数据。*

### Step 2: 重新创建数据表 (Recreate Tables)
删除数据表后，使用 Alembic 迁移工具重新创建所有表。

在 `backend` 目录下运行:
```bash
alembic upgrade head
```

### Step 3: 重新回填新字段数据 (Re-run Data Backfill)
创建表后，运行数据回填脚本以初始化新增字段的数据。

在 `backend` 目录下运行:
```bash
python scripts/backfill_repo_metadata.py
```

### Step 4: 重新同步 GitHub 数据 (Re-sync GitHub Data)
最后，运行数据同步脚本，从 GitHub 获取最新的仓库信息。

在 `backend` 目录下运行:
```bash
python scripts/sync_data.py
```

完成以上步骤后，您的数据库将被完全重置，并填充了最新的数据和结构。
