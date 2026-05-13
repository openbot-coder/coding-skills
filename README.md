# coding-skills

轻量级 AI 编程技能系统。

## 概述

`coding-skills` 是一套轻量级 AI 编程工作流，核心理念：**设计文档是项目的唯一真相源（SSOT），AI 凭此可重建整个项目**。

```
阶段0: 项目初始化 → design.md 就绪 → 阶段1-5 变更循环（每需求一次）

阶段0: 项目初始化（仅一次）
  绿地 --init → 创建完整骨架
  棕地 --adopt → 扫描已有代码

阶段1: 需求分析 → 阶段2: 任务拆解 → 阶段3: 代码执行 → 阶段4: 测试验证 → 阶段5: 需求归档
```

## 特点

- **零依赖**：仅使用 Python 标准库
- **跨平台**：Windows、macOS、Linux
- **模块化**：多个独立技能，按需使用
- **AI 友好**：SKILL.md 作为路由器，AI 助手加载后自动引导

## 核心技能

| 技能 | 用途 | 说明 |
|------|------|------|
| `code-exploration` | 代码探索 | 修改代码前先理解代码库 |
| `vibe-coding` | AI编程工作流 | 阶段0 初始化 + 五阶段变更循环 |
| `scripts-coding` | 脚本编程规范 | 规范脚本开发流程 |
| `skill-builder` | 技能构建器 | 创建和验证 Agent Skills |

## 项目结构

```
coding-skills/
├── SKILL.md                    # 主入口：技能路由器
├── README.md                   # 项目文档
├── LICENSE                     # 许可证

├── code-exploration/           # 代码探索子技能
│   └── SKILL.md                # 代码探索指南

├── vibe-coding/                # AI编程工作流（核心）
│   ├── SKILL.md                # 主入口：阶段0 + 五阶段变更循环
│   ├── README.md               # vibe-coding 文档
│   ├── scripts/                # 核心脚本工具
│   │   ├── design.py           # 阶段0：初始化(--init/--adopt) + 阶段1：需求分析(--change/--rollback)
│   │   ├── common.py           # 通用工具：find_project_root / detect_project_info 等
│   │   ├── changelog.py        # Changelog 管理：版本标记、状态更新
│   │   ├── plans.py            # 阶段2：任务拆解
│   │   ├── execute.py          # 阶段3：代码执行（TDD）
│   │   ├── verify.py           # 阶段4：测试验证
│   │   └── archive.py          # 阶段5：需求归档
│   ├── initialize/             # 项目初始化子技能
│   ├── writing-design/         # 需求调研子技能
│   ├── review-design/          # 设计审查子技能
│   ├── task-breakdown/         # 任务拆解子技能
│   ├── test-driven-development/ # TDD子技能
│   └── debugging-and-verification/ # 验证调试子技能

├── scripts-coding/             # 脚本编程规范
│   ├── SKILL.md                # 技能定义
│   ├── templates/              # 脚本模板
│   │   └── python_script_template.py
│   └── references/             # 参考文档
│       └── script-guidelines.md

├── skill-builder/              # 技能构建器
│   ├── SKILL.md                # 技能构建指南
│   ├── scripts/                # 辅助脚本
│   ├── references/             # 参考文档
│   └── assets/                 # 模板资源

└── security-audit/             # 安全审计
```

## 快速开始

### vibe-coding 工作流

**两种模式：**
- **模式 A（推荐）** — 中央 `docs/design.md` 作为唯一真相源，需求变更直接修改
- **模式 B（旧）** — 每个需求独立的 `{name}-design.md`，向后兼容

#### 阶段0：项目初始化（仅一次）

```bash
cd vibe-coding

# 绿地项目（全新空白目录）
python scripts/design.py --init --name "my-project" --lang python --desc "项目描述"

# 棕地项目（已有代码，自动扫描项目信息）
python scripts/design.py --adopt

# 棕地项目（指定项目名和起始版本）
python scripts/design.py --adopt --name "my-project" --version 1.0.0
```

初始化完成后，`docs/design.md` 和 `docs/changelog.md` 就绪，进入变更循环。

#### 阶段1：需求分析

```bash
# 模式 A：编辑 design.md 后记录变更
python scripts/design.py --change --desc "添加暗色模式" --bump minor

# 模式 B（旧）：创建独立变更文档
python scripts/design.py --name add-dark-mode --desc "添加暗色模式支持"
```

编辑 `docs/design.md`（模式 A）或 `{name}-design.md`（模式 B）。

#### review-design：设计审查

AI 先**完整读取设计文档**，逐章审查完整性、一致性、可执行性。审查通过后请求用户批准。

#### 阶段2：任务拆解

```bash
python scripts/plans.py --name add-dark-mode
```

编辑 `{name}-progress.md`，填充任务清单。

#### 阶段3：代码执行

```bash
# 查看任务
python scripts/execute.py --name add-dark-mode --action list

# 开始任务
python scripts/execute.py --name add-dark-mode --task T1 --action start

# 完成任务
python scripts/execute.py --name add-dark-mode --task T1 --action done
```

#### 阶段4：测试验证

```bash
python scripts/verify.py --name add-dark-mode --action start
python scripts/verify.py --name add-dark-mode --action done
```

#### 阶段5：需求归档

```bash
python scripts/archive.py --name add-dark-mode
```

### scripts-coding 脚本编程

使用 `scripts-coding/templates/python_script_template.py` 创建规范的脚本文件：

```bash
cp scripts-coding/templates/python_script_template.py scripts/my-script.py
```

命名规范：`{YYYYMMDD}-{代码用途}-{version}.py`

## 子技能详细说明

### code-exploration - 代码探索

**核心原则：** 修改代码前必须先理解代码库。

**功能：**
- 系统化探索项目结构、模块依赖、关键函数
- 使用 graphify 生成知识图谱
- 生成代码探索报告
- 支持多种编程语言（Python、JavaScript/TypeScript、Go、Rust 等）

**使用时机：**
- 开始新任务时
- 修改陌生模块或文件时
- 重构现有代码时
- 修复 bug 时

### vibe-coding - AI编程工作流

**整体流程：**

| 阶段 | 脚本 | 输入 | 输出 |
|------|------|------|------|
| **0. 项目初始化** | `design.py` | `--init` / `--adopt` | `docs/design.md` + `docs/changelog.md` + 项目骨架 |
| **1. 需求分析** | `design.py` | `--change` / `--name` | design.md 更新 / `{name}-design.md` |
| **2. 任务拆解** | `plans.py` | design.md | `{name}-progress.md` |
| **3. 代码执行** | `execute.py` | `{name}-progress.md` | 更新任务状态 |
| **4. 测试验证** | `verify.py` | `{name}-progress.md` | 验证结果 |
| **5. 需求归档** | `archive.py` | 用户已批准 | git tag + 归档 |

**两种模式：**
- **模式 A（推荐）：** 中央 `docs/design.md` → git tag 版本与 design.md 同步
- **模式 B（旧）：** 独立 `{name}-design.md` + `{name}-progress.md` → 归档到 `archive/`

**子技能：**
- `initialize` - 项目初始化（阶段0，一次）
- `writing-design` - 需求调研
- `review-design` - 设计审查（先完整读取 design.md，再逐章评审）
- `task-breakdown` - 任务拆解
- `test-driven-development` - TDD开发
- `debugging-and-verification` - 验证调试

### scripts-coding - 脚本编程规范

**核心功能：**
- 脚本存放目录规范（`scripts/` 长期，`tmp/` 临时）
- 文件命名规范：`{YYYYMMDD}-{代码用途}-{version}.py`
- Python 脚本模板，包含完整日志配置
- 日志格式：`YYYY-MM-DD HH:MM:SS - LEVEL - filename:line - Message`
- ERROR 级别日志自动包含执行信息和堆栈跟踪
- 日志目录自动检测，支持 Agent 记忆系统集成

### skill-builder - 技能构建器

**核心功能：**
- 技能发现与需求分析
- 技能类型选择（simple、api-wrapper、document-processor、dev-workflow、research-synthesizer、code-exploration）
- 目录结构初始化（SKILL.md、scripts/、references/、assets/）
- SKILL.md 模板生成，包含标准 frontmatter 格式
- 技能验证与质量检查

**工作流程：**
1. **Discovery** - 理解技能需求和触发条件
2. **Archetype Selection** - 选择技能类型
3. **Initialization** - 创建目录结构
4. **Customization** - 编写技能内容
5. **Validation** - 验证技能结构

**目录结构：**
```
skill-builder/
├── SKILL.md                # 技能构建指南
├── scripts/                # 辅助脚本
├── references/             # 参考文档
└── assets/                 # 模板资源
```

## 开发原则

1. **先思考再编码** — 明确假设，暴露困惑，不确定就提问
2. **简洁优先** — 用最少的代码解决问题
3. **精准修改** — 只动必须动的，匹配现有风格
4. **目标驱动执行** — 定义可验证的成功标准

### 工程原则

5. **Hyrum's Law** — 行为的每个细节都是公共 API
6. **Chesterton's Fence** — 不要删除你不理解的东西
7. **测试金字塔** — 70% 单元测试 + 20% 集成测试 + 10% E2E 测试
8. **Beyoncé 规则** — 喜欢一个工具就该为它贡献
9. **左移原则** — 越早发现问题，修复成本越低
10. **二八定律** — 80% 的问题来自 20% 的代码区域

## AI 集成

将 `SKILL.md` 的内容添加到 AI 编程助手的系统提示中，AI 将自动按阶段引导开发过程。

支持的 AI 编程工具：

| 工具 | 集成方式 |
|------|----------|
| Claude Code | 通过 CLAUDE.md 加载 |
| Cursor | 通过 .cursorrules 或 Custom Instructions |
| Windsurf | 通过 Cascade Rules |
| GitHub Copilot | 通过 Workspace Instructions |
| Trae IDE | 通过 Skill 加载 |

## 参考项目

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — 轻量级 AI 规格文档框架

## Changelog

### v0.8.0 (2026-05-13)

**结构调整：**
- 将项目初始化拆分为**阶段0**（仅一次），与阶段1-5变更循环明确分离
- 绿地 `--init` 和棕地 `--adopt` 归入阶段0，不再是阶段1的一部分
- 阶段1仅保留 `--change`（需求变更）和 `--rollback`（版本回退）

**新增/改进：**
- `design.py` 同时处理阶段0（--init/--adopt）和阶段1（--change/--rollback）
- `find_project_root()` 检测支持扩展（package.json / Cargo.toml / go.mod）
- `detect_project_info()` 改用 `elif` 链，避免语言被后匹配文件错误覆盖
- `review-design` 子技能更新：强制要求**先完整读取 design.md** 再审查，支持模式 A 全局章节检查

**Bug 修复：**
- 修复 `changelog.py` 中 `find_tag_for_version` 的内联 import，改为模块级导入
- 删除 `DESIGN_TEMPLATE_B` 死代码（已被 `generate_greenfield_design()` 替代）

### v0.7.0 (2026-05-09)

**新功能：**
- 新增 `skill-builder` 技能构建器
- 支持技能类型选择
- 提供完整的技能开发工作流
- 技能验证与质量检查功能

### v0.6.0 (2026-05-09)

**新功能：**
- 新增 `scripts-coding` 脚本编程规范技能
- 提供 Python 脚本模板，包含完整日志配置
- 日志格式增强

### v0.5.0 (2026-05-03)

**新功能：**
- 新增 `code-exploration` 代码探索子技能
- 支持 graphify 生成交互式知识图谱

### v0.4.0 (2026-05-02)

**新功能：**
- 重构为单一 vibe-coding 轻量级 5 阶段工作流
- 参考 OpenSpec 设计理念

### v0.3.0 (2026-04-28)

**新功能：**
- 新增阶段：PRD 与详细设计

### v0.2.0 (2026-04-27)

**新功能：**
- 添加版本号到 SKILL.md
- 添加 6 条工程原则

### v0.1.0 (2026-04-26)

- 初始版本发布

## License

MIT
