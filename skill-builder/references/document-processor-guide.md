# 文档处理器技能指南

## 概述

文档处理器技能处理特定文件格式，并提供提取、转换和分析操作。

## 使用场景

- 处理 PDF 文档
- 分析 Excel 电子表格
- 解析 CSV 文件
- 转换文档格式
- 提取文本和元数据

## 目录结构

```
document-processor-skill/
├── SKILL.md
├── scripts/
│   ├── parser.py           # 文档解析逻辑
│   └── extractor.py        # 数据提取
├── references/
│   └── format_spec.md      # 格式规范
└── assets/
    └── templates/          # 输出模板
```

## Frontmatter 模板

```yaml
---
name: pdf-processor
description: "从 PDF 文件中提取文本和表格，填写表单，合并文档。在处理 PDF 文档或文档提取任务时使用。"
version: 1.0.0
license: MIT
compatibility: 需要 PyPDF2 或 pdfplumber
metadata:
  author: dev-team
  category: document-processing
  tags: [pdf, extraction, documents]
---
```

## 核心组件

### 1. 文档解析器

```python
# scripts/parser.py
import pdfplumber

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def extract_text(self):
        with pdfplumber.open(self.file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    def extract_tables(self):
        with pdfplumber.open(self.file_path) as pdf:
            tables = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                tables.extend(page_tables)
        return tables
```

### 2. 输出格式

- 文本提取
- 表格提取（CSV、JSON）
- 元数据提取
- 图像提取
- 文档转换

### 3. 处理流程

1. **输入**：接受文件路径或内容
2. **解析**：提取结构化数据
3. **转换**：转换为所需格式
4. **输出**：返回或保存结果

## 使用示例

```markdown
# PDF 处理器

## 概述

此技能从 PDF 文档中提取文本和表格。

## 功能特性

- 保持布局的文本提取
- 表格提取为 CSV 或 JSON
- 元数据提取（作者、日期、页数）
- 表单字段提取

## 使用方法

```python
from scripts.parser import PDFProcessor

# 处理 PDF
processor = PDFProcessor("document.pdf")

# 提取文本
text = processor.extract_text()

# 提取表格
tables = processor.extract_tables()
```

## 最佳实践

1. **内存管理**：高效处理大文件
2. **错误处理**：处理前验证文件格式
3. **输出选项**：支持多种输出格式
4. **性能**：优化大型文档处理
5. **格式支持**：处理不同版本的 PDF

## 支持的格式

- PDF（通过 pdfplumber、PyPDF2）
- DOCX（通过 python-docx）
- XLSX（通过 pandas、openpyxl）
- CSV（通过 csv 模块）
- JSON（内置）
