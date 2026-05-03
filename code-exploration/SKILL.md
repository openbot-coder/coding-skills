---
name: code-exploration
description: "代码探索技能 - 使用 graphify 增量探索。在修改代码前理解代码库结构。"
---

# Code Exploration — 代码探索

## 核心特性

**graphify 是本地增量更新，不消耗 token，可以随时使用。**

- 本地运行，无需 API 调用
- SHA256 缓存，只处理变更文件
- 持久化图谱，跨会话查询
- 自动增量更新

## 使用方式

### 标准方式（推荐）

```powershell
cd docs/vibe-coding
graphify update ../../
```

graphify 会在当前目录下生成 `graphify-out/`，即 `docs/vibe-coding/graphify-out/`。

### 其他命令

```bash
# 仅重新聚类现有图谱
cd docs/vibe-coding
graphify cluster-only ../../

# 查询图谱（BFS）
graphify query "问题"

# 查询图谱（DFS）
graphify query "问题" --dfs

# 查找两个概念之间的最短路径
graphify path "A" "B"

# 解释一个节点
graphify explain "节点"

# 查看交互式 HTML（在浏览器打开）
start graphify-out/graph.html
```

## 输出结构

```
docs/vibe-coding/
└── graphify-out/
    ├── graph.html          ← 交互式图谱（浏览器打开）
    ├── GRAPH_REPORT.md    ← 图谱分析报告
    ├── graph.json         ← 持久化图数据
    ├── cache/             ← SHA256 缓存
    └── manifest.json      ← 文件清单
```

## 查看报告

```powershell
type docs\vibe-coding\graphify-out\GRAPH_REPORT.md

start docs\vibe-coding\graphify-out\graph.html
```

## 安装（如果需要）

```bash
uv tool install graphifyy && graphify install
graphify trae-cn install
```

**注意：** PyPI 包名是 `graphifyy`（注意两个 y）

## 最佳实践

1. **开始新需求前**：`cd docs/vibe-coding && graphify update ../../`
2. **代码变更后**：同样命令更新图谱
3. **需要了解架构时**：读取 `docs/vibe-coding/graphify-out/GRAPH_REPORT.md`
4. **想找关系时**：使用 `graphify query/explain/path`

### 图谱报告包含什么

- **God Nodes** - 最核心的函数/类，连接最多
- **Communities** - 模块聚类
- **Surprising Connections** - 意外发现的关系
- **Knowledge Gaps** - 连接弱的部分，可能是文档缺失

## 完整工作流示例

```powershell
# 1. 更新图谱
cd docs/vibe-coding
graphify update ../../

# 2. 查看报告
type graphify-out\GRAPH_REPORT.md

# 3. 打开交互式可视化
start graphify-out\graph.html

# 4. 查询特定问题
graphify query "如何处理变更归档？"
```

## 与 vibe-coding 的集成

1. 回答架构问题前，读取 `docs/vibe-coding/graphify-out/GRAPH_REPORT.md`
2. 跨模块关系问题，使用 `graphify query/explain/path`
3. 代码修改后，在 `docs/vibe-coding/` 下运行 `graphify update ../../`

## 重新完整扫描

```powershell
cd docs\vibe-coding
Remove-Item -Recurse -Force graphify-out
graphify update ../../
```
