---
name: script-development
description: 当功能点 ≤ 50 且可用单一文件完成时的脚本类开发。无需文档，直接编写代码和单元测试。
---

# 脚本类代码开发

## 概述

适用于功能点 ≤ 50 的小型脚本或工具：

- **功能点估算**：≤ 50 FP
- **文件要求**：单一文件即可完成
- **文档要求**：无需文档
- **流程**：直接编写代码 + 单元测试

## 快速判断

| 问题 | 答案 | 判断 |
|------|------|------|
| 一个人能说清楚吗？ | 是 | 可能是脚本类 |
| 需要多人协作吗？ | 否 | 可能是脚本类 |
| 功能点估算 > 50 吗？ | 否 | 脚本类 |
| 需要模块拆分吗？ | 否 | 脚本类 |

## 开发流程

```
需求确认 → 编写代码 → 编写测试（正例+反例+边界值）→ 验证覆盖率 100% → 审查 → 完成
```

### 1. 需求确认

快速明确：
- **输入**：什么数据？
- **处理**：要做什么？
- **输出**：期望什么结果？

### 2. 编写代码

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
| 文档 | 无需 | 需要 PRD + 设计 |
| 流程 | 简化 | 完整 8 阶段 |
| 测试 | 单元测试 | 单元+集成+E2E |

## 示例

### Python 脚本示例

```python
def calculate_discount(price: float, discount_rate: float) -> float:
    """
    计算折扣价格
    
    Args:
        price: 原价
        discount_rate: 折扣率 (0-1)
    
    Returns:
        折后价格
    
    Raises:
        ValueError: 参数无效
    """
    if price < 0:
        raise ValueError("价格不能为负数")
    if not 0 <= discount_rate <= 1:
        raise ValueError("折扣率必须在 0-1 之间")
    
    return price * (1 - discount_rate)


# === 单元测试 ===
import pytest

class TestCalculateDiscount:
    # 正例测试
    def test_normal_discount(self):
        assert calculate_discount(100, 0.2) == 80.0
    
    def test_zero_discount(self):
        assert calculate_discount(100, 0) == 100.0
    
    def test_full_discount(self):
        assert calculate_discount(100, 1.0) == 0.0
    
    # 反例测试
    def test_negative_price(self):
        with pytest.raises(ValueError, match="价格不能为负数"):
            calculate_discount(-100, 0.2)
    
    def test_invalid_discount_rate(self):
        with pytest.raises(ValueError, match="折扣率必须在 0-1 之间"):
            calculate_discount(100, 1.5)
    
    # 边界值测试
    def test_minimum_price(self):
        assert calculate_discount(0.01, 0.5) == 0.005
    
    def test_boundary_discount_rate_zero(self):
        assert calculate_discount(100, 0) == 100.0
    
    def test_boundary_discount_rate_one(self):
        assert calculate_discount(100, 1.0) == 0.0
```

运行覆盖率：
```bash
pytest test_discount.py --cov=. --cov-report=term-missing --cov-report=term-missing
```

## 关键原则

1. **简洁优先** — 不做过度设计
2. **测试即文档** — 用测试描述预期行为
3. **覆盖率 100%** — 每行代码都要被测试覆盖
4. **边界值思维** — 考虑极端情况和非法输入
