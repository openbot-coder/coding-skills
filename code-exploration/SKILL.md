# code-exploration

## 概述

代码深度探索工具，将 **graphify（知识图谱）** 与 **agentgrep（即时搜索）** 结合，
提供从"点到面"的代码理解工作流。

> **核心理念**：用 agentgrep 发现代码结构 → 用 graphify 图谱发现关联 → 更深入理解代码架构

---

## 依赖

```bash
# graphify — 构建知识图谱
pip install graphifyy && graphify install

# agentgrep — 即时代码搜索（已预装）
agentgrep --version
```

---

## 整合工作流

### 1️⃣ 即时搜索 + 文件发现（agentgrep）

```bash
# 搜索代码
agentgrep grep "def handle_" --path <project>

# 发现文件
agentgrep find auth handler --path <project>

# 查看文件结构
agentgrep outline <project>/src/main.py

# 关系追踪
agentgrep trace subject:auth relation:validated --path <project>
```

### 2️⃣ 深度图谱分析（graphify）

```bash
# 构建/更新知识图谱
python scripts/explore.py

# 强制全量重扫
python scripts/explore.py --full

# 查看缓存状态
python scripts/explore.py --status
```

### 3️⃣ 点 → 面 结合探索

```
发现入口 → agentgrep find main handler
                ↓
查看结构 → agentgrep outline handler.py
                ↓
图谱关联 → graphify query "handler 相关的模块"
                ↓
关系追踪 → agentgrep trace subject:handler relation:calls
                ↓
扩散探索 → agentgrep find 找到的新模块...
```

---

## explore.py 升级命令

| 命令 | 说明 |
|------|------|
| `explore.py` | 默认增量扫描（graphify） |
| `explore.py --full` | 强制全量重扫 |
| `explore.py --status` | 查看缓存状态 |
| `explore.py --check` | 检查是否需要更新 |
| `explore.py --install-hooks` | 安装 Git hooks |
| `explore.py --quick` | **快速模式**：用 agentgrep 替代 graphify 做轻量扫描 |
| `explore.py --search <词>` | **即时搜索**：用 agentgrep grep 搜索代码 |
| `explore.py --find <词>` | **文件发现**：用 agentgrep find 发现文件 |
| `explore.py --trace <词>` | **关系追踪**：用 agentgrep trace 追踪关系 |
| `explore.py --outline <file>` | **结构概览**：用 agentgrep outline 查看文件结构 |
| `explore.py --graph-agent` | **图谱驱动搜索**：从 graphify graph.json 提取文件 → agentgrep 分析关联 |

---

## 实战场景

### 场景：理解一个新项目的认证模块

```bash
# 1. 快速扫描代码结构
python scripts/explore.py --quick

# 2. 找到认证相关的文件
python scripts/explore.py --find auth login

# 3. 查看关键文件结构
python scripts/explore.py --outline src/auth/handler.py

# 4. 搜索认证流程
python scripts/explore.py --search "def login"

# 5. 构建完整知识图谱（如果项目较大）
python scripts/explore.py

# 6. 查询图谱了解模块关系
graphify query "认证模块的依赖关系"

# 7. 关系追踪：查看认证模块调用了哪些函数
agentgrep trace subject:auth_handler relation:calls --path .
```

### 场景：重构旧模块

```bash
# 1. 图谱查询旧模块影响范围
graphify query "payment 模块影响的文件"

# 2. agentgrep 搜索所有依赖点
agentgrep grep "import.*payment" --path src/

# 3. 追踪调用链
agentgrep trace subject:payment_service relation:rendered --path .

# 4. 查看关键文件结构
agentgrep outline src/payment/service.py
```

---

## 原理

```
agentgrep（广度搜索）
    ↓
发现文件/代码结构
    ↓
graphify（深度图谱）
    ↓
发现关联关系/聚类
    ↓
agentgrep trace（关系追踪）
    ↓
扩散到更多相关代码
    ↓
循环：更深 → 更广 → 更深
```
