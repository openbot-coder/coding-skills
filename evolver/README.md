# Evolver — AHE-Style Self-Evolution Engine

基于复旦大学 Agentic Harness Engineering (AHE) 论文的自我进化引擎。

## 核心设计

**三大可观测性：**
- **组件可观测性** (`harness_map.py`): 哪些 harness 组件出了问题
- **经验可观测性** (`evidence_distiller.py`): 失败模式如何提炼
- **决策可观测性** (`manifest.py` + `verifier.py`): 每次修改都声明预期影响并验证

## 架构

```
evolution_loop
    ├── collector.py       # 从 traces/ 收集失败记录
    ├── evidence_distiller.py  # 蒸馏 failure_type + severity + frequency
    ├── evolution_agent.py  # 生成修改方案 + manifest
    ├── verifier.py        # 验证实际影响是否匹配预测
    └── manifest.py        # 修改声明 + 历史追踪
```

## CLI 用法

```bash
# 分析失败，生成 evidence
python -m evolver.cli analyze

# 运行完整进化循环（包含 propose + apply + verify）
python -m evolver.cli evolve

# 生成进化报告
python -m evolver.cli report

# 手动记录失败
python -m evolver.cli record --skill xxx --reason "..."

# 验证所有待审 manifest
python -m evolver.cli verify

# 展示统计数据
python -m evolver.cli stats
```

## Backward Compatibility

```bash
# 旧命令仍然可用
python scripts/self_evolve.py analyze
python scripts/self_evolve.py suggest
python scripts/self_evolve.py update-rules  # -> 提示使用新的 evolve 命令
```

## 目录结构

```
evolver/
├── manifests/   # 每次修改的 manifest 声明
├── evidence/    # 蒸馏后的 evidence
├── history/     # 进化循环运行历史
├── traces/      # 原始失败 traces
└── .evolver_edits/  # 待执行的修改指令
```

## 与原 self_evolve.py 的区别

| 原功能 | 新实现 |
|--------|--------|
| `analyze` (关键词匹配) | `distill()` (LLM 蒸馏 + 规则匹配) |
| `suggest` (生成建议) | `propose()` (生成 manifest + edit_instructions) |
| `update-rules` (手动规则更新) | `apply_proposal()` (manifest 声明 + verifier 验证) |

关键区别：**manifest 机制** — 每次修改都声明预期影响，不匹配则自动回滚。
