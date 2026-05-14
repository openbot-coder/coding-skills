---
version: 0.3.0
name: initialize
description: "项目初始化子技能。首次使用时判断项目类型（绿地/棕地），初始化后标记，已初始化项目跳过检查以节省 token。"
---

# Initialize — 项目初始化

## 设计原则

**已初始化项目跳过检查，减少 token 消耗。**

初始化完成后创建标记文件，后续使用直接进入阶段路由。

## 初始化流程

```
检查 docs/vibe-coding/.initialized 是否存在
         │
         ├── 存在 → ✅ 已初始化，跳过
         │
         └── 不存在 → 执行初始化
                      │
                      ├── 检查项目状态
                      ├── 绿地/棕地初始化
                      └── 创建 .initialized 标记
```

## Step 1: 检查初始化状态

```bash
# 检查标记文件是否存在
if [ -f "docs/vibe-coding/.initialized" ]; then
    echo "✅ 已初始化，跳过"
    # 直接进入阶段路由
else
    echo "📦 需要初始化"
    # 执行初始化流程
fi
```

**标记文件：** `docs/vibe-coding/.initialized`

文件内容（可选）：
```markdown
version: 1.0.0
initialized_at: YYYY-MM-DD
project_type: greenfield|brownfield
```

## Step 2: 判断项目类型

| 类型 | 定义 |
|------|------|
| **绿地项目** | 空项目或未开始写代码的项目 |
| **棕地项目** | 已有代码的项目 |

### 判断依据

```bash
git status
```

| Git 状态 | 项目类型 | 处理 |
|----------|----------|------|
| 不是 git 仓库 | 绿地（空项目） | 创建目录，提示初始化 git |
| 干净仓库（无文件） | 绿地 | 创建初始结构 |
| 干净仓库（已有提交） | 棕地 | 扫描代码库 |
| 有未提交的更改 | 棕地 | 先提交，打标签 |

## Step 3: 绿地项目初始化

**条件：** 干净的空仓库或无代码项目

```bash
# 1. 创建目录结构
mkdir -p docs/vibe-coding/changes/archive

# 2. 创建初始文件
touch docs/vibe-coding/{project-name}-design.md

# 3. 创建初始化标记
echo "version: 1.0.0" > docs/vibe-coding/.initialized
echo "initialized_at: $(date +%Y-%m-%d)" >> docs/vibe-coding/.initialized
echo "project_type: greenfield" >> docs/vibe-coding/.initialized

# 4. Git 提交
git add .
git commit -m "feat: 初始化 vibe-coding 项目结构"
```

**输出：**
```
✅ 绿地项目初始化完成
📁 docs/vibe-coding/
   ├── .initialized            ← 初始化标记
   └── {project-name}-design.md  ← 请编辑此文件
```

## Step 4: 棕地项目初始化

**条件：** 已有代码的项目

### 4.1 未提交代码处理

```bash
# 检查并提交未提交的代码
if [ -n "$(git status --porcelain)" ]; then
    echo "📦 发现未提交的代码，先提交"

    git add .
    git commit -m "chore: vibe-coding 初始化前提交现有代码"

    # 打标签方便回滚
    git tag vibe-coding-initialize
    git push origin --tags

    echo "✅ 已提交并打标签"
fi
```

### 4.2 代码库扫描

> 参考 [code-exploration skill](../code-exploration/SKILL.md)

使用 graphify 生成代码库分析报告：

```powershell
# 在 docs/vibe-coding 目录下运行，输出到 graphify-out/
cd docs/vibe-coding
graphify update ../../

# 查看报告
type graphify-out\GRAPH_REPORT.md
```

### 4.3 创建目录和文件

```bash
# 1. 创建目录结构
mkdir -p docs/vibe-coding/changes/archive

# 2. 创建初始化标记
echo "version: 1.0.0" > docs/vibe-coding/.initialized
echo "initialized_at: $(date +%Y-%m-%d)" >> docs/vibe-coding/.initialized
echo "project_type: brownfield" >> docs/vibe-coding/.initialized

# 3. 生成项目设计文档（基于 graphify 报告）
# 详见下方模板

# 4. Git 提交
git add .
git commit -m "feat: 初始化 vibe-coding 项目结构"
```

**输出：**
```
✅ 棕地项目初始化完成
📁 docs/vibe-coding/
   ├── .initialized              ← 初始化标记
   ├── {project-name}-design.md   ← 项目设计文档
   ├── graphify-out/             ← graphify 分析报告（由 graphify 命令生成）
   │   ├── graph.html
   │   ├── GRAPH_REPORT.md
   │   └── graph.json
   └── changes/
       └── archive/              ← 已归档变更
```

## 项目设计文档模板

```markdown
# {项目名称} 设计文档

## 项目概述

<!-- 根据 graphify-out/GRAPH_REPORT.md 填写 -->

## 架构

<!-- 根据 graphify-out/GRAPH_REPORT.md 填写 -->

## 技术栈

<!-- 根据 graphify-out/GRAPH_REPORT.md 中的 tech_stack 部分填写 -->

## 目录结构

<!-- 根据 graphify-out/GRAPH_REPORT.md 填写 -->

## 变更日志

| 日期 | 变更 | 负责人 | 归档文件 |
|------|------|--------|----------|
```

## 后续变更

每次变更归档时，更新 `{project-name}-design.md`：

```markdown
## 变更日志

| 日期 | 变更 | 负责人 | 归档文件 |
|------|------|--------|----------|
| YYYY-MM-DD | 初始项目 | - | - |
| YYYY-MM-DD | 变更名称 | - | add-feature/ |
```

## 项目名称确定

如果项目目录名称不符合项目含义，可使用：

1. 检查 `package.json` / `pyproject.toml` / `Cargo.toml` 中的项目名
2. 检查 `README.md` 中的项目名
3. 使用目录名作为默认值

## 重新初始化

如需重新初始化，删除 `.initialized` 文件：

```bash
rm docs/vibe-coding/.initialized
```

然后重新触发 vibe-coding，系统会重新执行初始化流程。
