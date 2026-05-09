## Scripts Coding Skill

### Overview
规范脚本程序的编写流程、存放位置、日志管理等内容，确保脚本开发的一致性和可维护性。

### Core Principles
1. **目录规范**：明确脚本存放位置，区分长期和临时脚本
2. **命名规范**：统一文件命名格式，便于管理和检索
3. **文档规范**：强制要求文件头部注释，记录关键信息
4. **日志规范**：统一日志记录和存放位置

### Directory Structure
```
项目根目录/
├── scripts/          # 长期使用的脚本
│   └── {脚本文件}
├── tmp/              # 临时使用的脚本（可定期清理）
│   └── {脚本文件}
└── .trash/
    └── logs/         # 脚本日志文件
```

### Script Placement Priority
1. 用户明确指定的存放位置
2. `scripts/` - 长期使用的脚本
3. `tmp/` - 临时使用的脚本
4. `.trash/` - 最终存放位置

### File Naming Convention
```
{创建日期}-{代码用途}-{标志}-{版本}
```
- **创建日期**：YYYYMMDD 格式
- **代码用途**：简短描述脚本功能
- **标志**：
  - `long` - 长期脚本
  - `temp` - 临时脚本
- **版本**：v1, v2, v3...（可选）

**Example:**
```
20260509-data-processing-long-v1.py
20260509-test-script-temp.py
```

### Script Template
脚本必须使用提供的模板编写，确保一致性。

### Log Management
- 日志文件存放在 `.trash/logs/` 目录
- 日志文件名格式：`{脚本名}.log`
- 记录内容：
  - 脚本调用时间
  - 输入参数
  - 执行结果
  - 错误信息

### Usage
```bash
# 创建长期脚本
python scripts-coding/scripts/create_script.py --name data-processor --type long

# 创建临时脚本
python scripts-coding/scripts/create_script.py --name quick-test --type temp
```

### References
- `templates/` - 脚本模板文件
- `references/` - 参考文档

---

## Workflow

### Step 1: Determine Script Type
询问用户脚本用途：
- 长期使用 → `scripts/`
- 临时使用 → `tmp/`

### Step 2: Check Directory Existence
检查目标目录是否存在，如不存在则询问用户是否创建。

### Step 3: Generate Script from Template
使用 `templates/python_script_template.py` 创建脚本文件。

### Step 4: Add Header Documentation
引导用户填写文件头部注释信息。

### Step 5: Set Up Logging
配置日志输出到 `.trash/logs/` 目录。

---

## Templates Available
- `templates/python_script_template.py` - Python 脚本模板

## References
- `references/script-guidelines.md` - 脚本编写详细指南