# 开发工作流技能指南

> **设计模式：** 🔄 Pipeline — 强制执行带检查点的严格多步骤工作流（也适用于 🔍 Reviewer 模式的自动化审查部分）

## 概述

开发工作流技能自动化开发任务，并在软件开发生命周期中强制执行最佳实践。

## 使用场景

- 自动化 Git 工作流
- 项目脚手架
- 代码生成
- 构建和部署自动化
- 测试和质量检查

## 目录结构

```
dev-workflow-skill/
├── SKILL.md
├── scripts/
│   ├── workflow.py         # 工作流编排
│   └── helpers.py          # 实用函数
├── references/
│   └── standards.md        # 编码标准
└── assets/
    └── templates/          # 项目模板
```

## Frontmatter 模板

```yaml
---
name: git-workflow
description: "自动化 Git 工作流，包括分支、合并和拉取请求管理。在管理 Git 仓库或实现 CI/CD 管道时使用。"
version: 1.0.0
license: MIT
compatibility: 需要 git CLI
metadata:
  author: dev-team
  category: development
  tags: [git, workflow, automation]
---
```

## 核心组件

### 1. 工作流编排

```python
# scripts/workflow.py
import subprocess

class GitWorkflow:
    def create_feature_branch(self, name):
        subprocess.run(["git", "checkout", "-b", f"feature/{name}"])
    
    def commit_with_message(self, message):
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", message])
    
    def push_to_remote(self, branch=None):
        branch = branch or self._get_current_branch()
        subprocess.run(["git", "push", "origin", branch])
```

### 2. 工作流模板

- **功能分支**：创建 → 开发 → PR → 审核 → 合并
- **发布流程**：分支 → 测试 → 标记 → 部署
- **热修复**：创建 → 修复 → 合并 → 部署

### 3. 自动化钩子

- 提交前钩子
- 提交消息验证
- 分支命名约定
- CI/CD 集成

## 使用示例

```markdown
# Git 工作流

## 概述

此技能自动化常见的 Git 工作流并强制执行最佳实践。

## 工作流程

### 功能开发

1. 创建功能分支：`feature/feature-name`
2. 使用规范消息提交更改
3. 推送到远程
4. 创建拉取请求
5. 审核并合并

### 发布流程

1. 创建发布分支：`release/v1.0.0`
2. 运行测试
3. 标记版本
4. 部署到生产环境

## 使用方法

```python
from scripts.workflow import GitWorkflow

workflow = GitWorkflow()
workflow.create_feature_branch("new-feature")
workflow.commit_with_message("feat: add new feature")
workflow.push_to_remote()
```

## 最佳实践

1. **分支命名**：使用一致的约定（feature/、bugfix/、release/）
2. **提交消息**：遵循规范提交格式
3. **代码审核**：合并前需要 PR 审核
4. **测试**：合并前运行测试
5. **文档**：随更改更新文档

## 分支策略

| 分支类型 | 模式 | 用途 |
|-------------|---------|---------|
| main | `main` | 生产就绪代码 |
| develop | `develop` | 集成分支 |
| feature | `feature/*` | 新功能 |
| bugfix | `bugfix/*` | 错误修复 |
| release | `release/*` | 发布准备 |
| hotfix | `hotfix/*` | 紧急修复 |
