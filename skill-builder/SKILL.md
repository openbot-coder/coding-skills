---
name: skill-builder
description: "从零创建高质量的 Agent Skills。当需要创建新技能、审查现有技能或优化技能配置时使用。支持 SKILL 审核机制（可用性 + 安全性）、审计日志系统、自我进化能力。"
---

# Skill Builder — 技能构建器 v3.0

## 概述

专业技能创建助手，帮助用户从零开始创建高质量的 Agent Skills。v3.0 引入 **5 种设计模式**贯穿技能创建全过程，每种模式对应一类常见技能场景。

**核心功能：**
- **Inversion 发现** — 先采访用户，再确定设计方向
- **5 种设计模式匹配** — 为技能选择最适合的架构（Tool Wrapper / Generator / Reviewer / Inversion / Pipeline）
- **Generator 模板生成** — 从可复用模板生成结构化 SKILL.md + 标准目录
- **Reviewer 审核** — 按严重程度（🔴严重/🟡高危/🟢建议）对照清单逐一评审
- **Pipeline 工作流** — 强制执行带检查点的多步骤管线
- **审计日志**（统一记录 + 统计 + 失败案例复盘）
- **自我进化**（失败模式分析 + 自动优化审核规则）

## Pipeline 工作流（带检查点）

> 此工作流采用 **Pipeline 设计模式**：每个阶段都有明确的入口条件（🔑 Gate）和出口检查点（✅ Checkpoint），未通过检查点不得进入下一阶段。

```
         🔑 Gate 1    🔑 Gate 2    🔑 Gate 3    🔑 Gate 4    🔑 Gate 5
            ↓            ↓            ↓            ↓            ↓
阶段1: Discovery → 阶段2: Pattern → 阶段3: Gen → 阶段4: 微调 → 阶段5: Review
            ✅ CP1       ✅ CP2       ✅ CP3       ✅ CP4       ✅ CP5
            ↓
        阶段6: Publish（审计日志）
            ↓
持续: Self-Evolution（失败分析 → 规则更新 → 模板优化）
```

### 🔑 Gate 1 — 用户有明确需求

### 阶段1：Inversion Discovery（反向发现）

> 采用 **Inversion 设计模式**：Agent 先采访用户，收集完整信息后再开始行动，而非直接假设用户需求。

依次向用户提出以下问题，**所有问题收集完毕后再进入下一阶段**：

**🎯 核心问题（采访式）：**
1. 这个技能用来解决什么问题？用户会用什么话来触发它？
2. 技能的主要使用者是谁？期望的输出是什么？
3. 需要调用外部 API、处理本地文件、执行代码，还是纯知识问答？
4. 存放位置？（个人 / 项目 / 插件）
5. 这个技能是一次性使用还是周期性运行？需要自动化调度吗？
6. 有没有需要特别注意的安全性考虑（凭证、敏感数据、文件权限）？

> 💡 在每个问题之后，等待用户回答并追问细节，不要一次性抛完问题。

### ✅ Checkpoint 1 — 需求文档已确认

### 🔑 Gate 2 — 用户已确认需求方向

### 阶段2：Design Pattern Matching（设计模式匹配）

根据上一轮的答案，为用户推荐的技能选择最合适的**设计模式**：

| 设计模式 | 适用场景 | 核心形态 | 映射参考指南 |
|:---------|:---------|:---------|:-------------|
| **Tool Wrapper** | 包装外部 API / CLI 工具，让 Agent 成为任何库的专家 | 一个 APIClient 类 + 标准化方法 + 错误/重试/限流 | [`references/api-wrapper-guide.md`](references/api-wrapper-guide.md) |
| **Generator** | 从模板生成结构化文档、代码脚手架、报告 | 模板文件 + 参数化填充 + 多格式输出 | [`references/document-processor-guide.md`](references/document-processor-guide.md) |
| **Reviewer** | 按严重程度逐项审查代码/配置/文档 | 检查清单 + 严重度分级 + 自动化扫描 | [`references/dev-workflow-guide.md`](references/dev-workflow-guide.md) |
| **Inversion** | 需求不明确、需要先收集大量信息的分析任务 | 采访引导流程 + 渐进式披露 + 确认闭环 | [`references/research-synthesizer-guide.md`](references/research-synthesizer-guide.md) |
| **Pipeline** | 严格的多步骤操作，每步依赖上一步的结果 | 阶段划分 + Gate/Checkpoint + 状态追踪 | 可结合多个模式，详见[`references/design-patterns-guide.md`](references/design-patterns-guide.md) |

> 每种模式的详细对比、选择决策图和组合指南请参阅 [`references/design-patterns-guide.md`](references/design-patterns-guide.md)

**选择逻辑：**
- 如果用户说"调用 XX API" → **Tool Wrapper**
- 如果用户说"生成报告/代码/文档" → **Generator**
- 如果用户说"审查/检查/审计" → **Reviewer**
- 如果用户说"分析/研究/总结" → **Inversion**
- 如果用户说"自动化流程/工作流" → **Pipeline**
- 如果用户说"处理文件/转换格式" → **Generator**（输出型）或 **Tool Wrapper**（工具型）

### ✅ Checkpoint 2 — 设计模式已确认

### 🔑 Gate 3 — 用户认可模式选择

### 阶段3：Generator — 目录 + 模板生成

> 采用 **Generator 设计模式**：从可复用模板生成标准化的目录结构和 SKILL.md。

根据选定的设计模式，生成对应的目录结构：

```
skill-name/
├── SKILL.md          # 必需：指令 + 元数据
├── scripts/          # 可选：可执行代码
├── references/       # 可选：文档参考
└── assets/           # 可选：模板、资源
```

### 阶段4：Frontmatter Schema（元数据模板）

生成标准的 SKILL.md frontmatter：

```yaml
---
name: skill-name
description: "What it does and when to use it. Include trigger keywords."
version: 1.0.0
license: MIT
compatibility: Requires git and jq
metadata:
  author: your-org
  category: development
  tags: [testing, automation]
---
```

| 字段 | 是否必需 | 约束 |
|---|---|---|
| `name` | 是 | 2-64 字符，小写/数字/连字符，必须匹配目录名 |
| `description` | 是 | 10-1024 字符，包含引号，描述 what + when |
| `version` | 否 | 语义版本（MAJOR.MINOR.PATCH） |
| `license` | 否 | 许可证名称或引用 |
| `compatibility` | 否 | 1-500 字符，环境要求 |
| `metadata` | 否 | 自定义字段对象 |

### ✅ Checkpoint 3 — 目录和模板已生成 → 交给用户微调

### 🔑 Gate 4 — 用户已完成内容微调

### 阶段4：Customization（微调）

根据选定的设计模式，引导用户对模板进行针对性修改：

| 设计模式 | 微调重点 |
|:---------|:---------|
| **Tool Wrapper** | 确认 API 端点、认证方式、重试/限流策略、方法签名 |
| **Generator** | 确认模板变量、支持格式、输出路径 |
| **Reviewer** | 确认检查项清单、严重度分级标准、修复建议格式 |
| **Inversion** | 确认采访问题列表、信息收集模板、输出结构 |
| **Pipeline** | 确认阶段数量、每个 Gate/Checkpoint 条件、状态追踪方式 |

### ✅ Checkpoint 4 — 技能内容已就绪

### 🔑 Gate 5 — 用户请求审核或内容完成度 > 80%

### 阶段5：Reviewer — 按严重程度审计

> 采用 **Reviewer 设计模式**：对照严重度分级的检查清单逐项审查，🔴 严重项不通过则阻断发布。

审核分为 **可用性（Quality）** 和 **安全性（Security）** 两个维度，每项检查标注严重程度：

#### 5.1 可用性审核（Quality Review）

| 严重度 | 检查项 | 内容 | 阻断 |
|:------:|:-------|:-----|:----:|
| 🔴 **严重** | 格式正确性 | front matter 完整性、YAML 语法、分隔符闭合 | 是 |
| 🔴 **严重** | 描述清晰度 | description 是否包含 `WHAT + WHEN`、触发词是否明确 | 是 |
| 🟡 **高危** | 业务流程连贯性 | 流程完整、无死循环、条件覆盖全面 | 建议 |
| 🟡 **高危** | 可执行性 | 引用的脚本/文档是否存在、路径是否正确 | 建议 |

#### 5.2 安全性审核（Security Review — 12+ 项检查）

| 严重度 | 检查项 | 危险信号 |
|:------:|:-------|:---------|
| 🔴 **严重** | 代码注入 | `exec()`、`eval()`、`__import__()`、`os.system()` |
| 🔴 **严重** | 凭证泄露 | 硬编码密码、API Key、Token、Secret、Access Key |
| 🔴 **严重** | 命令执行 | `shell=True`、反引号命令、`Popen` 不受控参数 |
| 🟡 **高危** | 路径穿越 | `../` 不受控文件路径操作 |
| 🟡 **高危** | 反序列化 | `pickle.loads()`、`yaml.load()`（无 SafeLoader） |
| 🟡 **高危** | SSRF | f-string 拼接 URL、用户输入直接拼接到请求 |
| 🟡 **高危** | 权限问题 | `sudo`、`chmod 777`、`rm -rf /` |
| 🟢 **建议** | 日志安全 | 日志中是否可能写出敏感信息 |
| 🟢 **建议** | 输入校验 | 用户输入是否有边界校验 |

**审核规则：**
- 🔴 **严重项有任意一项不通过** → 审核不通过，阻断发布，必须修复
- 🟡 **高危项超过 2 项不通过** → 建议修复后再发布
- 🟢 **建议项** → 记录到失败案例但不禁用发布

```bash
# 全量审核（可用性 + 安全性）
python scripts/review.py <skill-dir>

# 仅可用性审核
python scripts/review.py <skill-dir> --quality

# 仅安全性审核
python scripts/review.py <skill-dir> --security

# JSON 格式输出（用于脚本集成）
python scripts/review.py <skill-dir> --json
```

**适用于 Tool Wrapper / Generator 模式的额外检查：**
- 是否包含 API 认证说明（非硬编码凭证）
- 是否包含错误处理和重试逻辑（Tool Wrapper）
- 模板文件是否与 SKILL.md 内容一致（Generator）

### ✅ Checkpoint 5 — 审核通过，所有 🔴 严重项已清除

### 阶段6：Publish（发布）

审核通过后，记录审计日志并完成发布。

**Pipeline 模式的额外步骤：**
- 在日志中标注 Pipeline 状态（每个阶段 Gate/Checkpoint 的通过/失败时间）
- 为 Pipeline 技能添加阶段进度追踪能力

---

## 审计日志系统（Audit Log）

每次 SKILL 的创建、审核、调用都会记录到统一的日志系统，供统计和复盘。

```
logs/skill-audit/
├── skill-builder-audit.log        ← 每次 SKILL 创建/审核记录（JSON Lines）
├── skill-call-stats.json          ← 每日统计（通过/失败次数）
└── failure-cases/                 ← 失败案例 Md 文档
    ├── YYYYMMDD-HHMMSS-技能名.md
    └── ...
```

每条日志包含：时间戳、SKILL 名称、审核结果、检查明细、失败原因、调用来源。

```bash
# 查看统计
python scripts/audit_log.py stats

# 查看最近审核记录
python scripts/audit_log.py list

# 查看失败案例
python scripts/audit_log.py failures

# 手动记录
python scripts/audit_log.py record <skill-dir> --result pass --checks '{"...":{...}}'
```

## 自我进化（Self-Evolution）

基于审计日志和历史数据，实现技能的自动迭代。

### 分析失败模式

| 模式 | 描述 | 自动处理 |
|------|------|----------|
| **frontmatter 错误** | 必填字段缺失、分隔符错误 | 模板预检 + 自动修复 |
| **命名不规范** | name 不符合 kebab-case | 自动规范化函数 |
| **描述质量不足** | 缺少 WHEN/WHAT 信息 | 增加占位符提示 |
| **硬编码凭证** | SKILL 中包含密码/Token | 自动扫描标记 |
| **注入风险** | exec/eval 等危险函数 | 提供安全替代方案 |
| **资源缺失** | 引用不存在的脚本/文档 | 引用前文件存在性检查 |

```bash
# 分析失败模式
python scripts/self_evolve.py analyze

# 获取优化建议
python scripts/self_evolve.py suggest

# 根据历史数据自动生成新审核规则
python scripts/self_evolve.py update-rules

# 生成完整进化报告
python scripts/self_evolve.py report
```

### 工作流

```
开发新 SKILL → 审核（可用性+安全性）→ 日志记录
                                           ↓
                                   持续监控失败模式
                                           ↓
                                   自动更新审核规则
                                           ↓
                                   模板自动优化迭代
                                           ↓
                                   降低失败率 → 质量提升
```

## 使用流程（Pipeline 模式）

> 以下流程严格遵循 **Pipeline 设计模式**：每个步骤都有入口条件（Gate）和完成检查点（Checkpoint），未满足条件不能跳过。

### 步骤1：Inversion 采访（需求确认）

先回答 Agent 的采访问题，不要跳过。确认以下内容：
- 🎯 技能目标（WHAT + WHEN）
- 🧩 设计模式偏好（Tool Wrapper / Generator / Reviewer / Inversion / Pipeline）
- 🔐 安全性要求（凭证、敏感数据、文件权限）

### 步骤2：Generator — 初始化目录和模板

根据选定的设计模式生成目录结构：

```bash
# 创建技能目录
mkdir -p skills/your-skill-name

# 初始化基本结构
touch skills/your-skill-name/SKILL.md
mkdir -p skills/your-skill-name/{scripts,references,assets}
```

根据设计模式，参考对应指南：
- **Tool Wrapper** → `references/api-wrapper-guide.md`
- **Generator** → `references/document-processor-guide.md`
- **Reviewer** → `references/dev-workflow-guide.md`
- **Inversion** → `references/research-synthesizer-guide.md`
- **Pipeline** → 可组合多个模式

### 步骤3：生成 Frontmatter + 内容模板

```yaml
---
name: your-skill-name
description: "[WHAT] this skill does. [WHEN] to use it. [TRIGGER] keywords."
version: 1.0.0
license: MIT
metadata:
  author: your-name
  category: development
design-pattern: tool-wrapper  # 或 generator / reviewer / inversion / pipeline
---
```

### 步骤4：Reviewer 审核

```bash
# 全量审核（可用性 + 安全性）
python scripts/review.py skills/your-skill-name
```

### 步骤5：Publish 发布

```bash
# 审核通过后，记录日志
python scripts/audit_log.py record skills/your-skill-name --result pass --caller "skill-builder"
```

**审核不通过时** — 查看失败的具体 **🔴 严重项**，修复后重新审核。

## 最佳实践

### 1. 按设计模式选择策略

| 设计模式 | 适合 | 不适合 |
|:---------|:-----|:-------|
| **Tool Wrapper** | 明确的外部工具/API | 纯知识问答、生成型任务 |
| **Generator** | 输出结构化的文档/代码 | 交互式对话、实时操作 |
| **Reviewer** | 质量把关、安全检查 | 创造性写作、开放式探索 |
| **Inversion** | 需求模糊、深度分析 | 紧急任务、固定流程 |
| **Pipeline** | 多步骤、有依赖的流程 | 单次简单操作 |

### 2. 命名规范

- **目录名**：使用 kebab-case，如 `pdf-processing`
- **文件名**：使用小写字母和连字符
- **避免**：大写字母、下划线、连续连字符

### 3. 描述公式

**[WHAT] + [WHEN] + [TRIGGERS]**

```
description: "Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or document extraction."
```

### 4. 内容指南

1. **保持简洁**：上下文窗口是公共资源，只添加必要信息
2. **设置适当自由度**：根据任务脆弱性选择指导级别
3. **渐进式披露**：分层次加载信息（元数据 → SKILL.md → 资源文件）
4. **避免重复**：信息应存在于 SKILL.md 或 references 中，不要重复
5. **Pattern-Aware**：在 SKILL.md 中标注 `design-pattern` 字段，方便后续维护

### 5. 文件大小建议

- **SKILL.md**：保持在 500 行以内
- **References**：大型文档放入 references 目录
- **Scripts**：可执行代码放入 scripts 目录

## 设计模式示例

### 🛠 Tool Wrapper 模式

```markdown
---
name: stock-api-wrapper
description: "封装股票行情API，提供行情查询和K线获取能力。用户说\"查股价\"时触发。"
design-pattern: tool-wrapper
---
调用 `scripts/stock_api.py` 中的函数获取数据。
```

### 📄 Generator 模式

```markdown
---
name: report-generator
description: "从结构化数据生成Markdown/HTML报告。传入数据列名和值，自动渲染。"
design-pattern: generator
---
模板文件在 `assets/templates/` 中，用 `scripts/render.py` 填充。
```

### 🔍 Reviewer 模式

```markdown
---
name: config-auditor
description: "审查配置文件，按🔴严重/🟡高危/🟢建议报告安全问题。Use before deploying to production."
design-pattern: reviewer
---
对照 `references/checklist.md` 中的检查项逐一审核。
```

### 🎙 Inversion 模式

```markdown
---
name: requirement-analyzer
description: "先采访用户了解项目背景和痛点，再输出需求分析文档。"
design-pattern: inversion
---
按 Inversion 流程：提问 → 收集 → 确认 → 输出。
```

### 🔄 Pipeline 模式

```markdown
---
name: deploy-pipeline
description: "自动化部署：Build → Test → Deploy → Health Check，每步有Gate和Checkpoint。"
design-pattern: pipeline
---
阶段1: Build | 阶段2: Test | 阶段3: Deploy | 阶段4: Health

## 与其他技能的衔接

```
skill-builder (v3.0)
  │
  ├──→ Inversion: 采访用户 → 确认需求 → 匹配设计模式
  │
  ├──→ Generator: 模板 → 目录 → SKILL.md
  │
  ├──→ Reviewer: 审核（quality + security）→ 审计日志 → 发布
  │     ↑
  │     └── security-audit（可复用12+安全检查规则）
  │
  ├──→ Pipeline: Checkpoint追踪 → 多阶段状态管理
  │
  ├──→ scripts-coding（日志规范参考）
  │
  └──→ self-evolution（持续迭代优化）
           ↓
    vibe-coding → 需求分析 → ... → 归档
```

## 命令速查

| 操作 | 命令 |
|------|------|
| 全量审核 | `python scripts/review.py <skill-dir>` |
| 仅可用性审核 | `python scripts/review.py <skill-dir> --quality` |
| 仅安全性审核 | `python scripts/review.py <skill-dir> --security` |
| JSON 审核输出 | `python scripts/review.py <skill-dir> --json` |
| 查看审核统计 | `python scripts/audit_log.py stats` |
| 查看失败案例 | `python scripts/audit_log.py failures` |
| 分析失败模式 | `python scripts/self_evolve.py analyze` |
| 生成进化报告 | `python scripts/self_evolve.py report` |
| 更新审核规则 | `python scripts/self_evolve.py update-rules` |

## 5 种设计模式速查

| 模式 | 英文名称 | 一句话描述 |
|:-----|:---------|:-----------|
| 🛠 **工具封装** | Tool Wrapper | 让 Agent 瞬间成为任意库的专家 |
| 📄 **生成器** | Generator | 从可复用模板生成结构化文档 |
| 🔍 **审查器** | Reviewer | 按严重程度对照清单评审代码 |
| 🎙 **反转** | Inversion | Agent 先采访你，再开始行动 |
| 🔄 **流水线** | Pipeline | 强制执行带检查点的严格多步骤工作流 |

> 详细的模式对比和选择逻辑参考 [`references/design-patterns-guide.md`](references/design-patterns-guide.md)

## 参考资源

- [Agent Skills Specification](https://agentskills.io/specification)
- [GitHub Copilot Skills Documentation](https://github.github.io/awesome-copilot/learning-hub/creating-effective-skills/)
- [outfitter-dev/skillcraft](https://github.com/outfitter-dev/outfitter/tree/main/plugins/fieldguides/skills/skillcraft)
- [muranustb/skills-creator](https://github.com/muranustb/skills-create_skills/tree/main/skills/skills-creator)