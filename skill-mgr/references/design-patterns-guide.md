# Agent Skills 五种设计模式完整指南

> 本文档详细说明 Agent Skills 的五种设计模式，包含模式定义、适用场景、选择逻辑、最佳实践和示例。

---

## 总览

| 设计模式 | 英文名称 | 核心思想 | 一句话口诀 |
|:---------|:---------|:---------|:-----------|
| 🛠 **工具封装** | Tool Wrapper | 把外部能力包成标准化接口 | "万能适配器" |
| 📄 **生成器** | Generator | 模板 + 变量 → 结构化输出 | "填空作文本" |
| 🔍 **审查器** | Reviewer | 对照清单按严重度分级审查 | "安检扫描仪" |
| 🎙 **反转** | Inversion | Agent 先采访用户再行动 | "先问后做" |
| 🔄 **流水线** | Pipeline | 多阶段带检查点的严格工作流 | "工业流水线" |

---

## 🛠 Tool Wrapper（工具封装）

### 定义

将外部 API、CLI 工具、数据库或第三方库封装为 Agent 可直接调用的标准化接口。Agent 无需了解底层细节，只需调用约定好的方法名。

### 适用场景

- 调用 REST / GraphQL API
- 执行 CLI 命令/脚本
- 读写数据库
- 使用第三方 Python 库（如 `requests`、`pandas`）
- 包装 MCP 工具

### 核心结构

```
scripts/
├── api_client.py    ← 核心：一个类 + N 个方法
├── utils.py         ← 辅助：错误重试、限流、认证
references/
└── api_docs.md      ← API 端点文档
```

### 检查清单

| # | 检查项 | 严重度 |
|:-:|:-------|:------:|
| 1 | API Key 是否存储在环境变量而非硬编码？ | 🔴 |
| 2 | 是否实现了错误重试（指数退避）？ | 🟡 |
| 3 | 是否处理了速率限制（429）？ | 🟡 |
| 4 | 是否对用户输入做了边界校验（防注入）？ | 🔴 |
| 5 | 方法签名是否清晰（参数名称 + 类型 + 文档）？ | 🟢 |

### 示例

```python
# scripts/weather_api.py
import os, requests, time
from requests.exceptions import RequestException

class WeatherClient:
    """天气查询 API 封装"""
    BASE_URL = "https://api.weather.com/v1"
    
    def __init__(self):
        self.api_key = os.environ["WEATHER_API_KEY"]
    
    def get_forecast(self, city: str, days: int = 3) -> dict:
        """获取城市天气预报"""
        if not city or len(city) > 50:
            raise ValueError("Invalid city name")
        for attempt in range(3):
            try:
                resp = requests.get(
                    f"{self.BASE_URL}/forecast",
                    params={"city": city, "days": days, "key": self.api_key},
                    timeout=10
                )
                resp.raise_for_status()
                return resp.json()
            except RequestException as e:
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
```

---

## 📄 Generator（生成器）

### 定义

从预定义模板 + 参数化变量生成结构化的文档、代码、配置或报告。适用于输出格式固定、内容来源明确的任务。

### 适用场景

- 生成 Markdown / HTML 报告
- 代码脚手架（项目初始化）
- 配置文件生成（YAML / JSON / TOML）
- 数据渲染（表格、图表）
- 文档格式转换

### 核心结构

```
assets/
├── templates/
│   ├── report.md.j2        ← 模板文件
│   └── config.yaml.j2
scripts/
├── render.py               ← 渲染引擎
└── validators.py           ← 变量验证
```

### 检查清单

| # | 检查项 | 严重度 |
|:-:|:-------|:------:|
| 1 | 模板是否与 SKILL.md 中的说明一致？ | 🔴 |
| 2 | 所有模板变量是否都有默认值或必填标记？ | 🟡 |
| 3 | 是否支持多输出格式（至少 Markdown + 原始数据）？ | 🟢 |
| 4 | 输出文件路径是否可由用户指定（防覆盖）？ | 🟡 |
| 5 | 大文件是否使用流式写入而非全部加载到内存？ | 🟢 |

### 示例

```python
# scripts/render.py
import os, json
from datetime import datetime

def render_report(template: str, data: dict, output_dir: str = ".") -> str:
    """从模板和数据生成报告"""
    tmpl_path = os.path.join("assets", "templates", f"{template}.md")
    if not os.path.exists(tmpl_path):
        raise FileNotFoundError(f"Template not found: {tmpl_path}")
    
    with open(tmpl_path, "r") as f:
        content = f.read()
    
    # 简单模板渲染（实际可用 jinja2）
    for key, val in data.items():
        content = content.replace(f"{{{{{key}}}}}", str(val))
    
    out_path = os.path.join(output_dir, f"report_{datetime.now():%Y%m%d_%H%M%S}.md")
    with open(out_path, "w") as f:
        f.write(content)
    return out_path
```

---

## 🔍 Reviewer（审查器）

### 定义

按预先定义的检查清单，对代码、配置、文档或输出进行逐项审查，每条结果标注严重程度（🔴严重 / 🟡高危 / 🟢建议），不满足 🔴 条件则阻断。

### 适用场景

- 代码质量审核（Code Review）
- 安全审计（Security Audit）
- 配置合规检查
- 文档完整性检查
- PR / Merge Request 前置检查

### 核心结构

```
scripts/
├── review.py           ← 检查引擎
└── rules/              ← 规则目录
    ├── quality.json    ← 可用性规则
    └── security.json   ← 安全性规则
references/
└── checklist.md        ← 检查清单文档
```

### 严重度分级标准

| 严重度 | 标签 | 含义 | 是否阻断 |
|:------:|:----:|:-----|:--------:|
| 🔴 严重 | CRITICAL | 直接导致系统不安全、数据泄露或功能不可用 | 是 |
| 🟡 高危 | HIGH | 可能导致问题但需要特定条件触发 | 建议修复 |
| 🟢 建议 | SUGGESTION | 不符合最佳实践但暂无明显风险 | 不阻断 |

### 检查清单

| # | 检查项 | 严重度 | 检查方式 |
|:-:|:-------|:------:|:---------|
| 1 | 是否存在硬编码凭证（密码、Token、API Key）？ | 🔴 | 正则扫描 |
| 2 | 是否存在注入风险（exec/eval/os.system）？ | 🔴 | 正则扫描 |
| 3 | 是否存在路径穿越（../ 不受控路径）？ | 🟡 | 路径分析 |
| 4 | 是否存在敏感日志泄露？ | 🟢 | 模式匹配 |
| 5 | 是否存在权限过高操作（sudo/chmod 777）？ | 🟡 | 正则扫描 |
| 6 | description 是否包含 WHAT + WHEN + TRIGGER？ | 🔴 | 文本分析 |
| 7 | 引用的脚本/文件是否存在？ | 🟡 | 文件系统检查 |

---

## 🎙 Inversion（反转）

### 定义

传统的 Agent 工作流是"用户提问 → Agent 回答"，Inversion 将其反转：**Agent 先主动采访用户**，收集所有必要信息后，再开始执行任务。

适用于用户需求模糊、不明确或需要逐步澄清的场景。

### 适用场景

- 需求分析（用户不知道自己要什么）
- 故障诊断（需要逐步定位问题）
- 研究报告（先了解研究方向和边界）
- 项目规划（先了解背景和约束）
- 复杂配置（先了解环境和偏好）

### 工作流

```
用户请求 → Agent 提问1 → 用户回答 → Agent 追问 → ...
→ Agent 确认理解 → 用户确认 → Agent 开始执行 → 输出结果
```

### 采访问题设计原则

| 原则 | 说明 | 示例 |
|:-----|:-----|:-----|
| **渐进式** | 从宽到窄，先问大方向再问细节 | "需要分析什么行业？" → "关注哪些竞品？" |
| **可确认** | 每个答案后总结一次，让用户确认 | "我理解您需要分析 A、B、C 三家竞品，对吗？" |
| **有边界** | 给出选项而非开放式提问 | "输出格式偏好：Markdown、HTML 还是 PDF？" |
| **必要性** | 只问真正需要的问题，不要为了凑问题数 | — |

### 示例流程

```markdown
用户: "帮我做个竞品分析"

Agent: "好的，我先了解下背景：
1. 需要分析哪个行业或领域？
2. 主要关注哪些竞争对手？
3. 分析深度：概览、详细维度对比、还是深度调研？
4. 报告格式偏好：Markdown、HTML 还是 PDF？
5. 有没有时间范围限制？

请先回答第 1 个问题，我们逐步来。"
```

---

## 🔄 Pipeline（流水线）

### 定义

将复杂任务分解为多个明确阶段，每个阶段之间设置 **Gate（入口条件）** 和 **Checkpoint（出口校验点）**，确保前一阶段的输出满足质量要求后，才允许进入下一阶段。

### 适用场景

- 部署流程（Build → Test → Deploy → HealthCheck）
- 数据处理（Extract → Transform → Load）
- CI/CD 管道
- 复杂的多步骤审核流程
- 数据分析和建模

### 核心结构

```
Pipeline 阶段结构：
  🔑 Gate 1       🔑 Gate 2       🔑 Gate 3
     ↓               ↓               ↓
  Phase 1   →    Phase 2    →    Phase 3
     ✅ CP1          ✅ CP2          ✅ CP3
```

### 阶段定义模板

```
## Pipeline 阶段

### 🔑 Gate — [入口条件描述]
- [条件1：例如 "用户已提供源代码"]
- [条件2：例如 "环境变量已配置"]

### 阶段 N： [阶段名称]
[阶段描述和具体执行步骤]

### ✅ Checkpoint — [出口校验描述]
- [通过标准1]
- [通过标准2]
- [失败处理：如果未通过怎么办]
```

### 检查清单

| # | 检查项 | 严重度 |
|:-:|:-------|:------:|
| 1 | 每个阶段是否有明确的 Gate 条件？ | 🔴 |
| 2 | 每个阶段是否有 Checkpoint 校验？ | 🔴 |
| 3 | Checkpoint 失败时是否有回退/重试机制？ | 🟡 |
| 4 | 是否记录了每个阶段的执行状态（时间+结果）？ | 🟢 |
| 5 | 是否可以从失败的 Checkpoint 继续而非重新开始？ | 🟡 |

### 示例

```markdown
# Deployment Pipeline

## 🔑 Gate — 代码已合并到 main 分支

### 阶段1：Build
- 运行 npm run build
- 产物打包到 dist/

### ✅ Checkpoint — 构建产物大小 < 5MB && 无 TypeScript 错误

### 阶段2：Test
- 运行 npm run test
- 运行 npm run e2e

### ✅ Checkpoint — 测试覆盖率 > 80% && 所有测试通过

### 阶段3：Deploy
- 上传到 CDN
- 更新 Kubernetes deployment

### ✅ Checkpoint — Health check 返回 200 && 延迟 < 200ms
```

---

## 如何选择设计模式

### 快速决策图

```
用户需求
  ├─ 需要调用外部能力（API/CLI/库）？ → Tool Wrapper
  ├─ 需要输出结构化文档/代码？       → Generator
  ├─ 需要审查/审计/检查？            → Reviewer
  ├─ 需求模糊需要逐步澄清？          → Inversion
  ├─ 严格的多步骤流程？              → Pipeline
  └─ 兼具多种特征？                  → Pipeline 组合多个模式
```

### 组合模式指南

一个技能可以包含多个设计模式。常见的组合：

| 组合 | 示例 |
|:-----|:-----|
| **Inversion + Generator** | 先采访用户了解需求，再生成定制报告 |
| **Tool Wrapper + Pipeline** | Pipeline 每个阶段调用不同的 API（Build → Deploy → Monitor） |
| **Reviewer + Pipeline** | Pipeline 每个阶段结束时进行一次 Reviewer 审核 |
| **Tool Wrapper + Generator** | 调用 API 获取数据 → 模板渲染生成报告 |

### 反模式

| 反模式 | 问题 |
|:-------|:-----|
| 给无外部调用的技能硬套 Tool Wrapper | 增加不必要的复杂度 |
| Generator 模板中硬编码变量 | 违背 Generator 的参数化初衷 |
| Reviewer 不设置严重度分级 | 可执行性差，全是🔴等于没分 |
| Inversion 一次性抛所有问题 | 用户被信息淹没，应渐进式提问 |
| Pipeline 没有失败恢复路径 | 任何阶段失败都导致整个流程报废 |
