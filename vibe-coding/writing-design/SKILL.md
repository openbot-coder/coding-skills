---
version: 0.2.0
name: writing-design
description: "需求调研与设计编写。支持两种模式：模式A（中央 design.md 连续修改）和模式B（独立变更文档）。通过协作对话将想法转化为完整设计。"
---

# 需求调研与访谈

## 概述

通过自然的协作对话，帮助将想法转化为完整的设计内容。

**模式 A（推荐）**：维护一份中央 `docs/design.md`，所有需求变更直接在其上修改，版本号递增。
**模式 B（旧模式）**：每次变更创建独立 `{name}-design.md`。

首先了解当前项目上下文，然后逐一提问来细化想法。一旦理解了需求，展示解决方案并获得用户批准。

<HARD-GATE>
在展示解决方案并获得用户批准之前，不得调用任何实现技能、编写任何代码、搭建任何项目或采取任何实现行动。这适用于每个项目，无论看起来多么简单。
</HARD-GATE>

## 模式选择

### 判断使用哪种模式

1. 检查项目根目录是否存在 `docs/design.md`
2. 如果存在 → 使用模式 A（直接修改 design.md）
3. 如果不存在 → 检查用户意图：
   - 新项目 → 建议使用模式 A（`--init`）
   - 旧项目且已有 changes 目录 → 使用模式 B（向后兼容）

## 模式 A：中央 design.md 连续修改

### 操作流程

```bash
# 1. 首次创建（如果 design.md 不存在）
python scripts/design.py --init --name "项目名称" --desc "项目描述"

# 2. 需求变更时：直接编辑 design.md 对应章节

# 3. 编辑完成后，记录变更
python scripts/design.py --change --desc "新增XX需求" --bump minor

# 4. 变更类型：
#    --bump major  - 架构重构/不兼容变更
#    --bump minor  - 新增需求/修改设计
#    --bump patch  - bug修复/微调
```

### design.md 变更原则

1. **直接修改**：不创建新文件，直接编辑 design.md 对应章节
2. **版本递增**：每次有意义的变更后，运行 `--change` 递增版本号
3. **完整性**：修改后 design.md 仍然是完整的、可独立阅读的产品设计
4. **AI 可重建**：任何 AI 凭这份 design.md 可以重建整个项目

### 版本管理规则

| 变更类型 | 版本递增 | 示例 |
|----------|----------|------|
| 新增功能 | minor +1 | 1.0 → 1.1 |
| 修改需求 | minor +1 | 1.0 → 1.1 |
| 删除需求 | minor +1 | 1.0 → 1.1 |
| 架构重构 | major +1 | 1.0 → 2.0 |
| 仅修 bug，不改设计 | patch +1 | 1.0 → 1.0.1 |

## 模式 B：独立变更文档（旧模式）

### 操作流程

```bash
python scripts/design.py --name <变更名称> --desc "<简要描述>"
```

编辑 `{name}-design.md`，遵循原有流程。

## 需求访谈记录

**模式 A**：访谈记录在 `docs/design.md` 的"背景"或新增章节中，版本号递增记录在 `changelog.md`。

**模式 B**：访谈记录在 `docs/vibe-coding/changes/{name}/{name}-design.md` 的背景部分。

### 访谈模板

```markdown
## 需求访谈记录

### 需求要点

- [ ] [记录收集到的需求]

### 确认的设计方案

[展示的设计方案，包括架构、组件、数据流等]

### 待确认事项

- [ ] [待确认的问题]
```

## 检查清单

你必须为以下每一项创建任务并按顺序完成：

1. **探索项目上下文** — 检查文件、文档、最近的提交、design.md（如存在）
2. **提出澄清问题** — 一次一个，理解目的/约束/成功标准
3. **提出 2-3 种方案** — 包含权衡和你的推荐
4. **展示解决方案** — 按复杂度分节展示，每节后获得用户批准
5. **记录访谈内容** — 模式A：更新 design.md + --change；模式B：更新 {name}-design.md
6. **过渡到审查** — 完成 writing-design，准备进入 review-design 阶段

## 流程图

```dot
digraph writing-design {
    "检查 design.md 是否存在" [shape=diamond];
    "模式A：编辑 design.md" [shape=box];
    "模式B：创建变更文档" [shape=box];
    "探索项目上下文" [shape=box];
    "提出澄清问题" [shape=box];
    "提出2-3种方案" [shape=box];
    "展示解决方案" [shape=box];
    "用户批准方案？" [shape=diamond];
    "记录变更 (--change)" [shape=box];
    "记录到变更文档" [shape=box];
    "过渡到审查阶段" [shape=doublecircle];

    "检查 design.md 是否存在" -> "模式A：编辑 design.md" [label="存在"];
    "检查 design.md 是否存在" -> "模式B：创建变更文档" [label="不存在"];
    "模式A：编辑 design.md" -> "探索项目上下文";
    "模式B：创建变更文档" -> "探索项目上下文";
    "探索项目上下文" -> "提出澄清问题";
    "提出澄清问题" -> "提出2-3种方案";
    "提出2-3种方案" -> "展示解决方案";
    "展示解决方案" -> "用户批准方案？";
    "用户批准方案？" -> "展示解决方案" [label="否，修改"];
    "用户批准方案？" -> "记录变更 (--change)" [label="是，模式A"];
    "用户批准方案？" -> "记录到变更文档" [label="是，模式B"];
    "记录变更 (--change)" -> "过渡到审查阶段";
    "记录到变更文档" -> "过渡到审查阶段";
}
```

**终止状态是完成 writing-design，准备进入 review-design 阶段。** 不要跳到实现阶段。

## 关键原则

- **一次一个问题** — 不要用多个问题淹没用户
- **优先选择题** — 可能的话比开放式更容易回答
- **严格执行 YAGNI** — 从所有设计中移除不必要的功能
- **探索替代方案** — 在确定之前总是提出 2-3 种方案
- **增量验证** — 展示方案，在继续之前获得批准
- **保持灵活** — 有不明白的地方随时回去澄清
- **记录为王** — 所有访谈必须记录，不记录的需求视为未确认
- **design.md 是唯一真相源** — 所有变更直接在其上修改，不是创建新文件

## 与 vibe-coding 的衔接

writing-design 完成后，进入 **需求分析阶段**：

```
writing-design → 需求分析 → review-design → 任务拆解 → 代码执行 → 测试验证 → 需求归档
```

**模式 A 需求分析阶段操作：**
1. 直接编辑 `docs/design.md` 对应章节
2. 运行 `python scripts/design.py --change --desc "变更描述" --bump minor`
3. 确认设计文档完整后，进入 review-design 阶段

**模式 B 需求分析阶段操作：**
1. 运行 `python scripts/design.py --name <变更名称>` 创建设计目录
2. 将 writing-design 记录的需求要点填入 `{name}-design.md`
3. 补充目标、成功标准、范围等设计内容
4. 确认设计文档完整后，进入 review-design 阶段