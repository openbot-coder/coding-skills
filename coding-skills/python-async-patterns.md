# Python 异步开发实战模式

> 来源：BotGateway 项目开发经验总结

## 1. 异步框架中的阻塞 I/O

**问题**：FastAPI/asyncio 中直接调用同步阻塞操作（如 DuckDB 写入）会卡死事件循环，导致所有并发请求排队等待。

**模式**：用 `asyncio.to_thread()` 将阻塞操作卸载到线程池。

```python
class LoggingDB:
    def _execute_insert(self, sql: str, values: list) -> None:
        """在线程池中执行的阻塞写入"""
        conn = self._get_conn()
        conn.execute(sql, values)

    async def log_request(self, **kwargs) -> None:
        """异步接口 — 不阻塞事件循环"""
        sql, values = self._build_insert(kwargs)
        await asyncio.to_thread(self._execute_insert, sql, values)
```

**判断标准**：async 上下文中执行时间 > 1ms 且不是 await 的操作，就是在阻塞。

## 2. SSE 流式异常捕获

**问题**：`StreamingResponse` 的生成器在 try/except 外执行，生成器内部的异常无法被外层捕获。

**错误做法**：在生成器内调用可失败的异步操作。
```python
async def _handle_stream(...):
    async def generate():
        stream_iter = await provider.chat_completions(...)  # ❌ 异常无法被外层捕获
        async for chunk in stream_iter:
            yield chunk
    return StreamingResponse(generate(), ...)
```

**正确做法**：在进入生成器前调用可失败的异步操作。
```python
async def _handle_stream(...):
    stream_iter = await provider.chat_completions(...)  # ✅ 异常可被外层 try/except 捕获

    async def generate():
        async for chunk in stream_iter:
            yield chunk
    return StreamingResponse(generate(), ...)
```

**原理**：`StreamingResponse` 创建后立即返回，生成器在后续才被迭代。生成器内的异常发生在请求体发送过程中，此时 HTTP 状态码已发送，无法再返回错误响应。

## 3. deque 固定大小滑动窗口

**问题**：滑动窗口限流用列表推导 `[t for t in records if t > window_start]` 每次重建，O(n) 复杂度。

**模式**：`deque` 预填零值 + `maxlen` 自动淘汰，仅检查链头，O(1)。

```python
class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = {}

    def is_allowed(self, key: str) -> bool:
        if self.max_requests <= 0:
            return False

        now = time.monotonic()
        window_start = now - self.window_seconds

        if key not in self._requests:
            # 预填 max_requests 个 0，利用 maxlen 自动淘汰
            self._requests[key] = deque([0.0] * self.max_requests, maxlen=self.max_requests)

        dq = self._requests[key]
        if dq[0] <= window_start:  # 链头超时 → 有空位
            dq.append(now)          # append 自动淘汰链头
            return True
        return False                # 链头未超时 → 窗口已满
```

**适用场景**：所有限流/频率统计/最近 N 条记录场景。

## 4. 持久连接 vs 每次新建

**问题**：每次数据库操作都 `connect() → execute() → close()`，连接开销大。

**模式**：懒初始化 + 持久连接 + 显式 `close()`。

```python
class LoggingDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._init_db()  # 建表仍用临时连接

    def _get_conn(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self._conn = duckdb.connect(self.db_path)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
```

**注意**：`_init_db()` 建表仍用临时连接，避免未初始化时创建持久连接。

## 5. 测试铁律 + 三维度

**铁律一**：测试用例必须覆盖正例/反例/边界值。
**铁律二**：单元测试覆盖率 100%，未覆盖行必须标注原因。
**铁律三**：集成测试同样三维度覆盖 + 全部自动化。

```python
# ── 正例 ──
def test_allows_within_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    assert limiter.is_allowed("key1") is True

# ── 反例 ──
def test_blocks_over_limit():
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.is_allowed("key1")
    limiter.is_allowed("key1")
    assert limiter.is_allowed("key1") is False

# ── 边界值 ──
def test_max_requests_zero():
    limiter = RateLimiter(max_requests=0, window_seconds=60)
    assert limiter.is_allowed("key1") is False
```

**异步测试**：用 `@pytest.mark.asyncio`，不要用已弃用的 `asyncio.get_event_loop().run_until_complete()`。

**未覆盖代码**：必须以注释标注原因（防御性代码、框架限制等），不可写"太难测试"。
