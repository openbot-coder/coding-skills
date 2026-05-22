# Vibe-Coding 自我升级指南

基于 [AHE 论文](https://arxiv.org/abs/2604.25850) 实现的自我进化功能。

## 概述

vibe-coding 通过三个可观测性支柱实现自我升级：

| 支柱 | 说明 | 实现 |
|------|------|------|
| **Component Observability** | 组件可观测性 | 子技能目录化，Git 版本控制 |
| **Experience Observability** | 经验可观测性 | 轨迹记录、证据收集、分析报告 |
| **Decision Observability** | 决策可观测性 | 变更清单配对预测和验证 |

## 目录结构

```
.vibe-coding/evolution/
├── evidence/                          # 证据语料库
│   ├── iteration-{N}/                 # 第 N 次迭代
│   │   ├── tasks/                    # 任务记录
│   │   ├── trajectories/             # 执行轨迹
│   │   ├── analysis.md               # 迭代分析
│   │   └── overview.md               # 迭代概览
│   └── analysis/                      # 分析报告
│       └── iteration-{N}_analysis.md  # 分析报告
├── change-manifests/                  # 变更清单
│   └── iteration-{N}_manifest.md      # 变更清单
└── evolve-log.md                      # 进化日志
```

## 进化循环

```
┌─────────────────────────────────────────────────────────────┐
│  1. 收集证据 (collect-evidence.py)                          │
│     - 记录任务开始/完成                                     │
│     - 记录执行轨迹                                          │
│     - 生成迭代概览                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 分析轨迹 (analyze-trajectories.py)                      │
│     - 提取成功/失败模式                                     │
│     - 分类错误类型                                          │
│     - 生成分析报告                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 变更决策 (change-manifest)                              │
│     - 识别问题                                              │
│     - 提出改进方案                                          │
│     - 预测效果                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 验证结果                                                │
│     - 验证改进效果                                          │
│     - 记录经验教训                                          │
│     - 决定保留或回滚                                        │
└─────────────────────────────────────────────────────────────┘
```

## 使用方法

### 1. 初始化进化

```bash
cd {项目目录}
python scripts/evolve.py --project-dir . --action init
```

### 2. 收集证据

```bash
# 记录任务开始
python scripts/collect-evidence.py --project-dir . --iteration 1 --action start-task --task-name T1 --task-type implementation

# 记录轨迹
python scripts/collect-evidence.py --project-dir . --iteration 1 --action trajectory --task-name T1 --phase design --content "设计完成"

# 记录任务完成
python scripts/collect-evidence.py --project-dir . --iteration 1 --action complete-task --task-name T1 --status Completed --duration 120.5

# 生成概览
python scripts/collect-evidence.py --project-dir . --iteration 1 --action overview
```

### 3. 分析轨迹

```bash
python scripts/analyze-trajectories.py --project-dir . --iteration 1 --action report
```

### 4. 运行完整进化循环

```bash
python scripts/evolve.py --project-dir . --action cycle
```

### 5. 更新变更清单

```bash
python scripts/evolve.py --project-dir . --action update --iteration 1 --manifest-update '{"status": "Applied"}'
```

## 触发条件

| 类型 | 触发条件 | 说明 |
|------|----------|------|
| **手动触发** | 执行 `evolve.py --action init` | 用户主动触发 |
| **自动触发** | 连续 3 次相同类型错误 | 系统自动触发 |
| **定时触发** | 每周/每月 | 定时任务触发 |

## 变更清单模板

每次技能修改必须填写变更清单，包含：

1. **Self-Declared Prediction**: 预测本次修改的效果
2. **Component Edits**: 修改的组件和内容
3. **Verification Plan**: 验证计划
4. **Verification Results**: 验证结果
5. **Lessons Learned**: 经验总结

详见 [`change-manifest-template.md`](change-manifest-template.md)

## 与 SKILL.md 的集成

vibe-coding 主技能在以下时机自动调用进化功能：

- 每次阶段切换时记录证据
- 每次任务完成时记录轨迹
- 每次发现问题时记录分析
- 每次修改规则时创建变更清单

## 最佳实践

### 证据收集

- ✅ 每个任务都要记录开始和结束
- ✅ 关键阶段都要记录轨迹
- ✅ 遇到错误时要详细记录上下文

### 变更决策

- ✅ 每次修改都要有明确的预测
- ✅ 预测要量化（提升 X%、减少 Y%）
- ✅ 无效的修改要及时回滚

### 经验积累

- ✅ 定期回顾进化日志
- ✅ 识别反复出现的问题
- ✅ 将有效做法固化为规则
