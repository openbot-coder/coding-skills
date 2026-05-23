# SDD Unit Development

> Phase 2 → AI 自驱动：接收任务列表，逐个完成设计 → 实现 → 测试

## 何时使用

- 任务拆解已完成（`progress.md` 中任务清单已确定）
- 当前阶段为 `🔄 进行中`

## 核心理念

**Spec-Driven Development（规范驱动开发）**：

```
写规范 → 写实现 → 写测试
```

每个任务必须按此顺序执行，不允许跳过。

## 执行流程

### Step 1：选择下一个任务

从 `progress.md` 中选择状态为 `⬜ 待执行` 的第一个任务。

### Step 2：为任务编写 SDD 规范

在任务详情中补充：

```markdown
### T{n}: {任务名称}

#### 接口定义
```python
def function_name(arg1: Type1, arg2: Type2) -> ReturnType:
    """简短描述"""
```

#### 行为约定
1. 当 `arg1` 为空时，抛出 `ValueError`
2. 当 `arg2` 为负数时，返回 `None`
3. 正常情况下返回计算结果

#### 边界条件
- `arg1 = None` → 抛出 `ValueError("arg1 cannot be None")`
- `arg2 < 0` → 返回 `None`
- `arg1 = ""` → 抛出 `ValueError`
- `arg2 = 0` → 返回 `0`

#### 错误处理
- 异常类型：`ValueError`, `TypeError`, `RuntimeError`
- 错误信息：清晰描述问题原因
```

### Step 3：实现代码

按照规范编写生产代码。

**原则**：
- 只实现规范中定义的内容
- 不添加规范外的"优化"
- 保持代码简洁

### Step 4：编写单元测试

按照 **正例 + 反例 + 边界值** 三覆盖原则：

```python
class TestFunctionName:
    """T{n} 测试套件"""

    # 正例
    def test_normal_case(self):
        assert function_name("hello", 5) == "hello" * 5

    # 反例
    def test_arg1_none_raises(self):
        with pytest.raises(ValueError, match="arg1 cannot be None"):
            function_name(None, 5)

    def test_arg2_negative_returns_none(self):
        assert function_name("hello", -1) is None

    # 边界值
    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            function_name("", 5)

    def test_zero_returns_zero(self):
        assert function_name("hello", 0) == ""
```

### Step 5：运行测试

```bash
# 单个任务测试
pytest tests/test_module.py::TestClass::test_name -v

# 全部测试
pytest -v --tb=short
```

### Step 6：更新进度

- 在 `progress.md` 中将任务状态改为 `✅ 已完成`
- 记录实际完成时间
- 如有阻塞，记录问题

## 覆盖率要求

| 模块 | 最低覆盖率 |
|------|-----------|
| 核心业务逻辑 | 100% |
| 工具函数 | 95% |
| 边界处理 | 100% |

## 提交规则

每个任务完成后自动提交 Git：

```bash
git add -A
git commit -m "feat: T{n} {任务名称}"
git push origin develop
```

## 任务完成判断

任务标记为完成需满足：

1. ✅ SDD 规范已编写
2. ✅ 生产代码已实现
3. ✅ 单元测试已编写（覆盖率达标）
4. ✅ 测试全部通过
5. ✅ Git 已提交

## 全部任务完成后

更新 `progress.md`：

```markdown
## 阶段状态

| 阶段 | 状态 | 开始时间 | 完成时间 |
|------|------|----------|----------|
| 需求定义 | ✅ 已批准 | - | - |
| 任务拆解 | ✅ 已完成 | 2026-05-23 10:00 | 2026-05-23 10:30 |
| SDD 开发 | ✅ 已完成 | 2026-05-23 10:30 | 2026-05-23 14:00 |
| 集成测试 | ⬜ 待执行 | - | - |
| 最终验收 | ⬜ 待执行 | - | - |
```

## 反模式

- ❌ 先写代码后补测试
- ❌ 测试覆盖率 < 100%
- ❌ 实现与规范不一致
- ❌ 一次处理多个任务
- ❌ Git 不提交或提交信息不清晰

## 触发条件

当 `progress.md` 中存在 `⬜ 待执行` 任务时，自动执行本技能。
