***

version: 0.1.0
name: scripts-coding
description: "脚本编程规范技能 - 规范脚本程序的编写流程、存放位置、日志管理等内容，确保脚本开发的一致性和可维护性。"
-------------------------------------------------------------------------------------------

# Scripts Coding — 脚本编程规范

## 概述

规范脚本程序的编写流程、存放位置、日志管理等内容，确保脚本开发的一致性和可维护性。

**核心原则：**
1. **目录规范**：明确脚本存放位置，区分长期和临时脚本
2. **命名规范**：统一文件命名格式，便于管理和检索
3. **文档规范**：强制要求文件头部注释，记录关键信息
4. **日志规范**：统一日志记录和存放位置

## 目录结构

```
项目根目录/
├── scripts/          # 长期使用的脚本
│   └── {脚本文件}
├── tmp/              # 临时使用的脚本（可定期清理）
│   └── {脚本文件}
└── logs/             # 脚本日志文件
```

## 脚本存放优先级

1. 用户明确指定的存放位置
2. `scripts/` - 长期使用的脚本
3. `tmp/` - 临时使用的脚本

## 文件命名规范

```
{创建日期}-{代码用途}-{版本}
```

- **创建日期**：YYYYMMDD 格式
- **代码用途**：简短描述脚本功能
- **版本**：v1, v2, v3...（可选）

**示例：**
```
20260509-data-processing-v1.py
20260509-quick-test.py
```

## 脚本模板

脚本必须使用提供的模板编写，确保一致性。模板包含：
- 文件头部注释（作者、日期、目的、背景、使用范围、功能）
- 日志配置（包含文件名和行号）
- 错误处理和异常日志记录

## 日志管理

### 日志格式

```
YYYY-MM-DD HH:MM:SS - LEVEL - filename:line - Message
```

**示例：**
```
2026-05-09 10:00:00 - INFO - my_script.py:42 - Processing data...
2026-05-09 10:00:01 - ERROR - my_script.py:105 - Error occurred
```

### ERROR 级别日志

ERROR 级别及以上自动包含执行信息和堆栈跟踪：

```
2026-05-09 10:00:01 - ERROR - my_script.py:105 - Error occurred: FileNotFoundError
Traceback (most recent call last):
  File "my_script.py", line 100, in process_file
    with open(filename, 'r') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'input.txt'
```

### 日志目录

- 默认日志目录：`logs/`
- 如果目录不存在，询问用户指定日志存放地址
- 将用户指定的日志地址记录到 Agent 记忆系统
- 下次使用时优先使用记忆中的目录

## 使用流程

### 步骤1：确定脚本类型

询问用户脚本用途：
- 长期使用 → `scripts/`
- 临时使用 → `tmp/`

### 步骤2：检查目录存在性

检查目标目录是否存在，如不存在则询问用户是否创建。

### 步骤3：使用模板生成脚本

使用 `templates/python_script_template.py` 创建脚本文件。

### 步骤4：添加头部文档

引导用户填写文件头部注释信息。

### 步骤5：设置日志配置

配置日志输出到 `logs/` 目录。

## 可用模板

- `templates/python_script_template.py` - Python 脚本模板

## 参考文档

- `references/script-guidelines.md` - 脚本编写详细指南