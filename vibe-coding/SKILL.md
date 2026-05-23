# Vibe Coding

> 人管两头，AI 跑中间：需求审批 → AI 自驱动循环 → 最终验收

## 概述

`vibe-coding` 是一套面向 AI 编程助手的轻量级开发工作流。

**核心理念**：
- **人管两头**：需求定义和最终验收必须由人审批
- **AI 跑中间**：任务拆解、设计、开发、测试由 AI 自驱动完成

## 工作流

```
Phase 0: 需求定义（人）
   ↓
Phase 1: 任务拆解（AI）
   ↓
Phase 2: SDD 开发（AI）
   ↓
Phase 3: 调试验证（AI）
   ↓
Phase 4: 最终验收（人）
   ↓
Phase 5: 归档（AI）
```

## 技能目录

| 技能 | 阶段 | 执行者 | 说明 |
|------|------|--------|------|
| `initialize/` | Phase 0 | AI | 初始化项目结构、需求模板 |
| `review-design/` | Phase 0 | AI + 人 | AI 自审 + 人工审批 |
| `task-breakdown/` | Phase 1 | AI | 需求 → 任务列表 + 优先级 |
| `writing-design/` | Phase 1 | AI | 生成详细设计文档 |
| `sdd-unit-development/` | Phase 2 | AI | 规范 → 实现 → 测试 |
| `debugging-and-verification/` | Phase 3 | AI | 测试失败 → 修复 → 重测 |
| `evolution/` | Phase 3-4 | AI | 收集证据、更新 manifest |
| `archive/` | Phase 5 | AI | 归档、打标签、创建 PR |

## 审批状态

`design.md` 中的审批状态是 AI 执行的唯一依据：

```markdown
## 审批状态

| 阶段 | 状态 | 审批人 | 时间 |
|------|------|--------|------|
| 需求定义 | ✅ 已批准 | 宝爷 | 2026-05-23 |
| 设计审查 | ✅ 已批准 | 宝爷 | 2026-05-23 |
| 最终验收 | ⏳ 待验收 | - | - |
```

**规则**：
- AI 看到 `✅ 已批准` → 自动进入下一阶段
- AI 看到 `⬜ 待执行` 或 `⏳ 待审批` → 等待人工
- AI 看到 `❌ 未通过` → 停止并报告问题

## 状态判断

通过检查文件和审批状态判断当前阶段：

| 文件状态 | 审批状态 | 当前阶段 | 下一步 |
|----------|----------|----------|--------|
| `design.md` 不存在 | - | 初始化 | 运行 initialize |
| `design.md` 存在 | 需求定义: ⬜ | 需求定义 | 等待用户填写 |
| `design.md` 存在 | 需求定义: ⏳ | 需求审查 | AI 自审 → 提交审批 |
| `design.md` 存在 | 需求定义: ✅ | 任务拆解 | AI 自动执行 task-breakdown |
| `progress.md` 有任务 | 设计审查: ✅ | SDD 开发 | AI 自动执行 sdd-unit-development |
| 所有任务完成 | 集成测试: ⬜ | 调试验证 | AI 自动执行 debugging-and-verification |
| 测试全部通过 | 最终验收: ⏳ | 最终验收 | 等待用户验收 |
| 用户已批准 | 最终验收: ✅ | 归档 | AI 自动执行 archive |

## 使用方式

### 1. 初始化项目

```bash
python scripts/design.py --init --name my-project --lang python
```

AI 自动执行 `initialize/` 技能，创建目录结构和模板。

### 2. 用户填写需求

用户编辑 `docs/vibe-coding/design.md`，填写：
- 背景、目标、范围
- 成功标准
- 用户故事

### 3. AI 自审 + 提交审批

AI 自动执行 `review-design/` 技能：
- 检查需求完整性
- 生成自审报告
- 更新审批状态为 `⏳ 待审批`
- 向用户展示设计摘要

### 4. 用户审批

用户在 `design.md` 中更新：

```markdown
| 需求定义 | ✅ 已批准 | 宝爷 | 2026-05-23 |
```

### 5. AI 自驱动循环

AI 自动执行：
1. `task-breakdown/` → 生成任务列表
2. `sdd-unit-development/` → 逐个完成任务
3. `debugging-and-verification/` → 测试验证
4. `evolution/` → 收集证据

### 6. 用户验收

AI 更新审批状态：

```markdown
| 最终验收 | ⏳ 待验收 | - | - |
```

向用户展示：
- 测试报告
- 变更总结
- 覆盖率数据

用户审批后：

```markdown
| 最终验收 | ✅ 已批准 | 宝爷 | 2026-05-23 |
```

### 7. AI 归档

AI 自动执行 `archive/` 技能：
- 提交 Git
- 打标签
- 创建 PR
- 移动目录

## 反模式

- ❌ AI 跳过审批直接开发
- ❌ 需求不完整就批准
- ❌ 测试不通过就验收
- ❌ 不更新审批状态
- ❌ 不收集证据

## 参考

- `README.md` — 完整文档
- `references/` — 架构原则、反模式、Git 规则
- `scripts/` — 辅助脚本
