# 研究综合器技能指南

> **设计模式：** 🎙 Inversion — Agent 先采访你，再开始行动

## 概述

研究综合器技能从多个来源收集信息，进行分析，并生成结构化报告或摘要。

## 使用场景

- 竞争分析
- 文献综述
- 市场研究
- 数据聚合
- 信息综合

## 目录结构

```
research-synthesizer-skill/
├── SKILL.md
├── scripts/
│   ├── researcher.py       # 研究逻辑
│   └── analyzer.py         # 分析功能
├── references/
│   └── sources.md          # 来源文档
└── assets/
    └── templates/          # 报告模板
```

## Frontmatter 模板

```yaml
---
name: competitive-analysis
description: "通过收集和综合竞争对手信息进行竞争分析。在研究市场趋势、竞争对手产品或行业格局时使用。"
version: 1.0.0
license: MIT
metadata:
  author: dev-team
  category: research
  tags: [analysis, research, competitive]
---
```

## 核心组件

### 1. 研究器类

```python
# scripts/researcher.py
import requests
from bs4 import BeautifulSoup

class Researcher:
    def __init__(self):
        self.sources = []
    
    def add_source(self, url):
        self.sources.append(url)
    
    def fetch_content(self, url):
        response = requests.get(url)
        return response.text
    
    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def synthesize(self):
        findings = []
        for source in self.sources:
            content = self.fetch_content(source)
            text = self.parse_html(content)
            findings.append({"source": source, "content": text})
        return findings
```

### 2. 分析技术

- **内容提取**：从来源提取关键信息
- **情感分析**：确定文本情感
- **主题建模**：识别主要主题
- **比较**：比较多个来源
- **摘要**：生成简明摘要

### 3. 输出格式

- Markdown 报告
- JSON 数据结构
- 可视化摘要
- 比较表格

## 使用示例

```markdown
# 竞争分析

## 概述

此技能收集竞争对手信息并生成结构化分析报告。

## 研究流程

1. **确定来源**：列出竞争对手网站、文章、评论
2. **收集信息**：获取并解析内容
3. **分析**：提取关键指标和洞察
4. **综合**：将发现整合到报告中

## 使用方法

```python
from scripts.researcher import Researcher

researcher = Researcher()
researcher.add_source("https://competitor1.com")
researcher.add_source("https://competitor2.com")

findings = researcher.synthesize()
```

## 最佳实践

1. **来源质量**：使用信誉良好的来源
2. **多样性**：从多个角度收集信息
3. **引用**：跟踪来源以供参考
4. **偏见意识**：考虑来源偏见
5. **时效性**：使用最新信息

## 报告结构

```markdown
# 竞争分析报告

## 执行摘要

发现的简要概述...

## 竞争对手

| 竞争对手 | 优势 | 劣势 |
|------------|-----------|------------|
| 竞争对手 A | 功能 X | 用户界面差 |
| 竞争对手 B | 低价 | 功能有限 |

## 关键发现

1. 发现 1
2. 发现 2
3. 发现 3

## 建议

基于分析...
```

## 信息来源

- 公司网站
- 行业报告
- 新闻文章
- 客户评论
- 社交媒体
- 技术文档
