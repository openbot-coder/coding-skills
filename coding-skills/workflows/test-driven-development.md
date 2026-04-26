---
name: test-driven-development
description: 在实现任何功能或修复 bug 时使用，在编写实现代码之前
---

# 测试驱动开发（TDD）

## 概述

先写测试。看它失败。写最少代码让它通过。

**核心原则：** 如果你没有看到测试失败，你不知道它测试的是否正确。

**违反规则的字面意思就是违反规则的精神。**

## 何时使用

**总是：**
- 新功能
- Bug 修复
- 重构
- 行为变更

**例外（需征得人类搭档同意）：**
- 一次性原型
- 生成代码
- 配置文件

在想"就这次跳过 TDD"？停下。那是合理化。

## 铁律

```
没有失败的测试就不能写生产代码
```

先写代码再写测试？删除它。从头开始。

**没有例外：**
- 不要保留它作为"参考"
- 不要在写测试时"适配"它
- 不要看它
- 删除就是删除

从测试出发重新实现。就这样。

## 红-绿-重构

```dot
digraph tdd_cycle {
    rankdir=LR;
    red [label="红\n编写失败测试", shape=box, style=filled, fillcolor="#ffcccc"];
    verify_red [label="验证正确\n失败", shape=diamond];
    green [label="绿\n最少代码", shape=box, style=filled, fillcolor="#ccffcc"];
    verify_green [label="验证通过\n全部绿色", shape=diamond];
    refactor [label="重构\n清理", shape=box, style=filled, fillcolor="#ccccff"];
    next [label="下一个", shape=ellipse];

    red -> verify_red;
    verify_red -> green [label="是"];
    verify_red -> red [label="错误\n失败"];
    green -> verify_green;
    verify_green -> refactor [label="是"];
    verify_green -> green [label="否"];
    refactor -> verify_green [label="保持\n绿色"];
    verify_green -> next;
    next -> red;
}
```

### 红 - 编写失败测试

编写一个最小测试展示应该发生什么。

<好>
```typescript
test('重试失败操作 3 次', async () => {
  let attempts = 0;
  const operation = () => {
    attempts++;
    if (attempts < 3) throw new Error('fail');
    return 'success';
  };

  const result = await retryOperation(operation);

  expect(result).toBe('success');
  expect(attempts).toBe(3);
});
```
名称清晰，测试真实行为，一件事
</好>

<坏>
```typescript
test('retry works', async () => {
  const mock = jest.fn()
    .mockRejectedValueOnce(new Error())
    .mockRejectedValueOnce(new Error())
    .mockResolvedValueOnce('success');
  await retryOperation(mock);
  expect(mock).toHaveBeenCalledTimes(3);
});
```
名称含糊，测试 mock 而非代码
</坏>

**要求：**
- 一个行为
- 清晰的名称
- 真实代码（除非不可避免否则不用 mock）

### 验证红 - 看它失败

**必须执行。绝不跳过。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试失败（而非报错）
- 失败消息是预期的
- 因为功能缺失而失败（而非拼写错误）

**测试通过了？** 你在测试已有行为。修改测试。

**测试报错了？** 修复错误，重新运行直到正确失败。

### 绿 - 最少代码

编写最简单的代码让测试通过。

<好>
```typescript
async function retryOperation<T>(fn: () => Promise<T>): Promise<T> {
  for (let i = 0; i < 3; i++) {
    try {
      return await fn();
    } catch (e) {
      if (i === 2) throw e;
    }
  }
  throw new Error('unreachable');
}
```
刚好够通过
</好>

<坏>
```typescript
async function retryOperation<T>(
  fn: () => Promise<T>,
  options?: {
    maxRetries?: number;
    backoff?: 'linear' | 'exponential';
    onRetry?: (attempt: number) => void;
  }
): Promise<T> {
  // YAGNI
}
```
过度工程
</坏>

不要添加功能、重构其他代码或"改进"超出测试范围的部分。

### 验证绿 - 看它通过

**必须执行。**

```bash
npm test path/to/test.test.ts
```

确认：
- 测试通过
- 其他测试仍然通过
- 输出干净（无错误、警告）

**测试失败了？** 修复代码，不是测试。

**其他测试失败？** 立即修复。

### 重构 - 清理

只在绿色之后：
- 移除重复
- 改善命名
- 提取辅助函数

保持测试绿色。不要添加行为。

### 重复

为下一个功能编写下一个失败测试。

## 好的测试

| 质量 | 好的 | 坏的 |
|------|------|------|
| **最小化** | 一件事。名称中有"和"？拆分它。 | `test('验证邮箱和域名和空格')` |
| **清晰** | 名称描述行为 | `test('test1')` |
| **展示意图** | 演示期望的 API | 遮蔽代码应该做什么 |

## 为什么顺序重要

**"我之后写测试来验证它有效"**

之后写的测试立即通过。立即通过什么都证明不了：
- 可能测试了错误的东西
- 可能测试了实现而非行为
- 可能遗漏了你忘记的边界情况
- 你从未看到它捕获 bug

先写测试迫使你看到测试失败，证明它确实测试了什么。

**"我已经手动测试了所有边界情况"**

手动测试是临时的。你以为测试了所有东西但：
- 没有记录你测试了什么
- 代码变更时无法重新运行
- 压力下容易忘记情况
- "我试的时候没问题" ≠ 全面

自动化测试是系统化的。它们每次以相同方式运行。

**"删除 X 小时的工作是浪费"**

沉没成本谬误。时间已经过去了。你现在的选择：
- 删除并用 TDD 重写（再 X 小时，高信心）
- 保留它并在之后添加测试（30 分钟，低信心，可能有 bug）

"浪费"是保留你无法信任的代码。没有真正测试的工作代码是技术债。

**"TDD 是教条主义的，务实意味着适应"**

TDD 就是务实的：
- 在提交前发现 bug（比之后调试更快）
- 防止回归（测试立即捕获破坏）
- 记录行为（测试展示如何使用代码）
- 启用重构（自由更改，测试捕获破坏）

"务实"的捷径 = 在生产中调试 = 更慢。

**"之后测试达到同样目标 - 是精神不是仪式"**

不。后测试回答"这做什么？"先测试回答"这应该做什么？"

后测试受你的实现偏见。你测试你构建的，而非所需的。你验证记住的边界情况，而非发现的。

先测试迫使在实现前发现边界情况。后测试验证你记住了一切（你没有）。

30 分钟的后测试 ≠ TDD。你获得了覆盖率，失去了测试有效的证明。

## 常见合理化

| 借口 | 现实 |
|------|------|
| "太简单不需要测试" | 简单代码也会坏。测试只需 30 秒。 |
| "我之后测试" | 测试立即通过什么都证明不了。 |
| "后测试达到同样目标" | 后测试 = "这做什么？" 先测试 = "这应该做什么？" |
| "已经手动测试过了" | 临时 ≠ 系统化。无记录，无法重新运行。 |
| "删除 X 小时是浪费" | 沉没成本谬误。保留未验证代码是技术债。 |
| "保留作为参考，先写测试" | 你会适配它。那是后测试。删除就是删除。 |
| "需要先探索" | 可以。扔掉探索，从 TDD 开始。 |
| "测试难 = 设计不清" | 倾听测试。难测试 = 难使用。 |
| "TDD 会让我变慢" | TDD 比调试更快。务实 = 先测试。 |
| "手动测试更快" | 手动无法证明边界情况。每次更改都要重新测试。 |
| "现有代码没有测试" | 你在改进它。为现有代码添加测试。 |

## 红线 - 停下并从头开始

- 先写代码再写测试
- 实现后写测试
- 测试立即通过
- 无法解释为什么测试失败
- "稍后"添加测试
- 合理化"就这次"
- "我已经手动测试过了"
- "后测试达到同样目的"
- "是精神不是仪式"
- "保留作为参考"或"适配现有代码"
- "已经花了 X 小时，删除是浪费"
- "TDD 是教条主义的，我很务实"
- "这不同因为..."

**所有这些意味着：删除代码。用 TDD 从头开始。**

## 示例：Bug 修复

**Bug：** 空邮箱被接受

**红**
```typescript
test('拒绝空邮箱', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

**验证红**
```bash
$ npm test
FAIL: expected 'Email required', got undefined
```

**绿**
```typescript
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  // ...
}
```

**验证绿**
```bash
$ npm test
PASS
```

**重构**
如果需要，为多个字段提取验证。

## 验证检查清单

在标记工作完成之前：

- [ ] 每个新函数/方法都有测试
- [ ] 在实现之前看到每个测试失败
- [ ] 每个测试因预期原因失败（功能缺失，而非拼写错误）
- [ ] 为每个测试编写了最少代码让它通过
- [ ] 所有测试通过
- [ ] 输出干净（无错误、警告）
- [ ] 测试使用真实代码（除非不可避免否则不用 mock）
- [ ] **铁律一：每个功能点覆盖正例 + 反例 + 边界值**
- [ ] **铁律二：单元测试覆盖率 100%，未覆盖行已标注原因**
- [ ] **铁律三：集成测试覆盖正例 + 反例 + 边界值，全部自动化**

无法勾选所有框？你跳过了 TDD。从头开始。

## 卡住时

| 问题 | 解决方案 |
|------|---------|
| 不知道怎么测试 | 写期望的 API。先写断言。问人类搭档。 |
| 测试太复杂 | 设计太复杂。简化接口。 |
| 必须模拟一切 | 代码太耦合。使用依赖注入。 |
| 测试设置庞大 | 提取辅助函数。仍然复杂？简化设计。 |

## 调试集成

发现 bug？编写复现它的失败测试。遵循 TDD 循环。测试证明修复并防止回归。

绝不没有测试就修复 bug。

## 测试反模式

添加 mock 或测试工具时，阅读 @testing-anti-patterns.md 避免常见陷阱：
- 测试 mock 行为而非真实行为
- 向生产类添加仅测试方法
- 在不理解依赖的情况下 mock

## 测试铁律

以下三条规则不可妥协，适用于所有项目，没有例外。

### 铁律一：三维度覆盖

测试用例必须覆盖正例、反例和边界值，缺一不可。

- **正例**：验证预期行为 — 正常输入 → 正常输出
- **反例**：验证错误处理 — 无效/非法输入 → 正确的错误响应
- **边界值**：验证临界行为 — 最小值、零值、空值、刚好等于/超过阈值

只有正例的测试 = 没有测试。只测了"能用"，没测"不能用"和"差点能用"。

### 铁律二：100% 单元测试覆盖率

单元测试代码覆盖率目标：**100%**。

每一行未覆盖的代码必须以行内注释标注无法覆盖的原因：

```python
# UNCOVERED: 防御性代码 — 此 NotImplementedError 仅在子类未实现时触发，
# 但所有子类均已实现，此行为路径不可达
raise NotImplementedError
```

**可接受的未覆盖原因：**
- 防御性代码（如抽象基类的 `NotImplementedError`）
- 框架架构限制（如流式生成器中的异常无法被外层 try/except 捕获）
- 第三方库内部路径
- 竞争条件中理论上可能但实践中不可复现的路径

**不可接受的未覆盖原因：**
- "太难测试"
- "太简单不需要"
- "之后补"
- "这个分支永远不会执行"

如果一行代码真的永远不执行，那它就不应该存在。删掉它。

### 铁律三：集成测试同样三维度 + 自动化

集成测试的测试用例也必须覆盖正例、反例和边界值，且必须落实自动化测试。

- **自动化**：所有集成测试可由 `pytest` 一键运行，无需手动步骤
- **可重复**：外部依赖（API 调用、数据库）全部通过 mock/临时实例隔离
- **三维度**：与单元测试相同，正例 + 反例 + 边界值

```
单元测试：每个函数/类 → 正例 + 反例 + 边界值 → 覆盖率 100%
集成测试：每条端到端链路 → 正例 + 反例 + 边界值 → 自动化可运行
```

## 测试三维度：正例、反例、边界值

每个功能点必须覆盖三个维度，缺一不可：

### 正例 — 验证预期行为
- 正常输入 → 正常输出
- 典型使用场景 → 功能正确完成
- 验证"它能做我们说它能做的事"

```python
def test_rate_limiter_allows_within_limit():
    """正例：限额内请求允许通过"""
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    assert limiter.is_allowed("key1") is True
```

### 反例 — 验证错误处理
- 无效输入 → 正确的错误响应
- 缺少必要参数 → 明确的错误信息
- 无权限访问 → 401/403 而非 500
- 验证"它不能做我们说它不能做的事"

```python
def test_rate_limiter_blocks_over_limit():
    """反例：超限请求被拒绝"""
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.is_allowed("key1")
    limiter.is_allowed("key1")
    assert limiter.is_allowed("key1") is False
```

### 边界值 — 验证临界行为
- 最小值、最大值、零值、空值
- 刚好等于阈值 vs 刚好超过阈值
- 并发/竞争条件（如果适用）

```python
def test_rate_limiter_max_requests_zero():
    """边界值：max_requests=0，所有请求被拒绝"""
    limiter = RateLimiter(max_requests=0, window_seconds=60)
    assert limiter.is_allowed("key1") is False

def test_rate_limiter_max_requests_one():
    """边界值：max_requests=1，首次通过第二次拒绝"""
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    assert limiter.is_allowed("key1") is True
    assert limiter.is_allowed("key1") is False
```

### 覆盖率要求

> 见 **铁律二**：100% 覆盖率，未覆盖行必须标注原因。

未覆盖代码的标注格式：

```python
# UNCOVERED: [原因分类] — [具体说明]
raise NotImplementedError  # 示例
```

| 原因分类 | 可接受 | 示例 |
|---------|--------|------|
| 防御性代码 | ✅ | 抽象基类 `NotImplementedError`，所有子类已实现 |
| 框架限制 | ✅ | 流式生成器异常无法被外层捕获 |
| 第三方路径 | ✅ | SDK 内部异常处理分支 |
| "太难" | ❌ | — |
| "太简单" | ❌ | — |
| "之后补" | ❌ | — |

## 异步测试模式

测试异步代码时使用 `pytest-asyncio`：

```python
import pytest

@pytest.mark.asyncio
async def test_async_db_write(tmp_path):
    """正例：异步数据库写入"""
    log_db = LoggingDB(str(tmp_path / "test.duckdb"))
    await log_db.log_request(request_id="req-1", status="success")
    # 验证数据已写入
```

**注意：**
- pytest-asyncio 严格模式下，异步测试必须加 `@pytest.mark.asyncio`
- 不要用 `asyncio.get_event_loop().run_until_complete()`（已弃用）
- 异步测试的 fixture 如果涉及共享资源（如数据库文件），确保使用 `tmp_path` 隔离

## 测试隔离

- 单元测试和集成测试使用独立的临时目录（`tmp_path`）
- 共享数据库文件会导致测试间冲突
- 每个测试创建自己的实例，不要跨测试共享状态

## 最终规则

```
生产代码 → 存在测试且测试先失败了
否则 → 不是 TDD
```

未经人类搭档许可没有例外。
