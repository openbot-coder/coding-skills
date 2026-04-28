---
name: script-development
description: 当功能点 ≤ 50 且可用单一文件完成时的脚本类开发。将文档说明写入代码文件头部，直接编写代码和单元测试。
---

# 脚本类代码开发

## 概述

适用于功能点 ≤ 50 的小型脚本或工具：

- **功能点估算**：≤ 50 FP
- **文件要求**：单一文件即可完成
- **文档要求**：将说明写入代码文件头部
- **流程**：直接编写代码 + 单元测试

## 核心原则

**文档即代码**：将功能说明、使用方法、示例直接写在代码文件开头，方便阅读和使用。

## 快速判断

| 问题 | 答案 | 判断 |
|------|------|------|
| 一个人能说清楚吗？ | 是 | 可能是脚本类 |
| 需要多人协作吗？ | 否 | 可能是脚本类 |
| 功能点估算 > 50 吗？ | 否 | 脚本类 |
| 需要模块拆分吗？ | 否 | 脚本类 |

## 开发流程

```
需求确认 → 编写头部文档 → 编写代码 → 编写测试（正例+反例+边界值）→ 验证覆盖率 100% → 完成
```

### 1. 需求确认

快速明确：
- **输入**：什么数据？
- **处理**：要做什么？
- **输出**：期望什么结果？

### 2. 编写头部文档

在代码文件开头用注释/文档字符串说明：

| 区块 | 内容 |
|------|------|
| 功能说明 | 这个脚本做什么，列出关键功能点 |
| 使用方法 | 命令行参数、API 调用方式 |
| 示例 | 常用场景的完整示例 |
| 依赖 | 运行环境、依赖库 |

### 3. 编写代码

直接编写实现代码，遵循简洁优先原则：
- 不做过度设计
- 不添加投机性代码
- 单文件完成

### 3. 编写测试

**覆盖率目标：100%**

| 测试类型 | 要求 |
|----------|------|
| 正例测试 | 正常输入，正常输出 |
| 反例测试 | 错误输入，错误处理 |
| 边界值测试 | 边界条件、极端值 |

### 4. 验证覆盖率

运行覆盖率工具，确保 100%：

```bash
# Python
pytest --cov=. --cov-report=term-missing --cov-report=term-missing

# JavaScript/TypeScript
jest --coverage

# Go
go test -coverprofile=coverage.out && go tool cover -func=coverage.out
```

### 5. 代码审查

- 检查代码逻辑
- 确认测试覆盖完整
- 验证边界条件处理

## 检查清单

- [ ] 需求已明确
- [ ] 代码已实现
- [ ] 正例测试已编写
- [ ] 反例测试已编写
- [ ] 边界值测试已编写
- [ ] 测试覆盖率 100%
- [ ] 代码审查通过

## 与其他流程的区别

| 对比项 | 脚本类 | 中小型/大型 |
|--------|--------|-------------|
| 功能点 | ≤ 50 | < 1000 / ≥ 1000 |
| 文档位置 | 代码文件头部 | 独立文档 (docs/) |
| 流程 | 简化 | 完整 8 阶段 |
| 测试 | 单元测试 | 单元+集成+E2E |

## 代码文件模板

将以下模板放在代码文件开头（各语言注释语法）：

```python
#!/usr/bin/env python3
"""
[功能名称]

功能说明：
- [功能点 1]
- [功能点 2]

使用方法：
    python this_script.py --input <输入文件> --output <输出文件>

示例：
    python this_script.py --input data.csv --output result.json

依赖：
- Python >= 3.8
- [其他依赖]

作者：[名字]
日期：YYYY-MM-DD
"""

import sys
import argparse
from typing import Optional

# === 实现代码 ===
# ... 你的代码 ...

# === 单元测试 ===
# ... 你的测试 ...
```

## 各语言示例

### Python

```python
#!/usr/bin/env python3
"""
折扣计算器

功能说明：
- 计算商品折后价格
- 支持百分比折扣和固定金额折扣
- 自动校验参数合法性

使用方法：
    from discount import calculate_percentage, calculate_fixed
    
    # 百分比折扣：原价 100，8 折
    result = calculate_percentage(100, 0.8)
    
    # 固定金额：原价 100，立减 20
    result = calculate_fixed(100, 20)

示例：
    >>> calculate_percentage(100, 0.8)
    80.0
    >>> calculate_fixed(100, 20)
    80.0

依赖：Python >= 3.8
"""

from typing import Union


def calculate_percentage(price: float, rate: float) -> float:
    """百分比折扣"""
    if price < 0:
        raise ValueError("价格不能为负数")
    if not 0 < rate <= 1:
        raise ValueError("折扣率必须在 0-1 之间")
    return price * rate


def calculate_fixed(price: float, discount: float) -> float:
    """固定金额折扣"""
    if price < 0:
        raise ValueError("价格不能为负数")
    if discount < 0:
        raise ValueError("优惠金额不能为负数")
    if discount > price:
        raise ValueError("优惠金额不能超过原价")
    return price - discount


# === 单元测试 ===
import pytest

class TestDiscount:
    """正例测试"""
    def test_percentage_normal(self):
        assert calculate_percentage(100, 0.8) == 80.0
    
    def test_fixed_normal(self):
        assert calculate_fixed(100, 20) == 80.0
    
    """反例测试"""
    def test_negative_price(self):
        with pytest.raises(ValueError):
            calculate_percentage(-100, 0.8)
    
    def test_discount_exceed_price(self):
        with pytest.raises(ValueError):
            calculate_fixed(100, 150)
    
    """边界值测试"""
    def test_zero_price(self):
        assert calculate_percentage(0, 0.8) == 0.0
```

### JavaScript/TypeScript

```typescript
/**
 * 数据验证工具
 * 
 * 功能说明：
 * - 验证邮箱格式
 * - 验证手机号格式
 * - 验证 URL 格式
 * 
 * 使用方法：
 * ```js
 * import { validateEmail, validatePhone, validateUrl } from './validator';
 * 
 * validateEmail('test@example.com'); // true
 * validatePhone('13812345678'); // true
 * ```
 * 
 * 依赖：Node.js >= 14
 */

/**
 * 验证邮箱格式
 */
function validateEmail(email: string): boolean {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

// === 单元测试 ===
import { describe, it, expect } from 'vitest';

describe('Validator', () => {
  // 正例测试
  it('valid email', () => {
    expect(validateEmail('test@example.com')).toBe(true);
  });
  
  // 反例测试
  it('invalid email', () => {
    expect(validateEmail('invalid')).toBe(false);
  });
  
  // 边界值测试
  it('email with plus', () => {
    expect(validateEmail('test+tag@example.com')).toBe(true);
  });
});
```

### Go

```go
// Package parser 提供 JSON 解析功能
//
// 功能说明：
//   - 解析 JSON 字符串为结构体
//   - 将结构体序列化为 JSON
//   - 支持自定义字段标签
//
// 使用方法：
//
//   result, err := ParseJSON[MyStruct](`{"name":"test"}`)
//
// 依赖：Go >= 1.18
package parser

import "encoding/json"

// ParseJSON 解析 JSON 字符串
func ParseJSON[T any](data string) (T, error) {
    var result T
    err := json.Unmarshal([]byte(data), &result)
    return result, err
}

// === 单元测试 ===
package parser

import (
    "testing"
)

func TestParseJSON(t *testing.T) {
    // 正例测试
    t.Run("valid json", func(t *testing.T) {
        result, err := ParseJSON[map[string]any](`{"name":"test"}`)
        if err != nil {
            t.Errorf("unexpected error: %v", err)
        }
        if result["name"] != "test" {
            t.Errorf("unexpected result: %v", result)
        }
    })
    
    // 反例测试
    t.Run("invalid json", func(t *testing.T) {
        _, err := ParseJSON[map[string]any](`{invalid}`)
        if err == nil {
            t.Error("expected error, got nil")
        }
    })
    
    // 边界值测试
    t.Run("empty object", func(t *testing.T) {
        result, _ := ParseJSON[map[string]any](`{}`)
        if len(result) != 0 {
            t.Errorf("expected empty map, got %v", result)
        }
    })
}
```

## 关键原则

1. **文档即代码** — 说明写在文件头部，方便阅读
2. **简洁优先** — 不做过度设计
3. **测试即文档** — 用测试描述预期行为
4. **覆盖率 100%** — 每行代码都要被测试覆盖
5. **边界值思维** — 考虑极端情况和非法输入
