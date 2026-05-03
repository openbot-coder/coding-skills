# CONTEXT.md 格式

项目领域术语定义文档的格式参考。

## 文件结构

```markdown
# {上下文名称}

{一两句话描述这个上下文是什么，为什么存在。}

## 语言

**{术语}**:
{简洁的定义，一句话}
_Avoid_: {避免使用的同义词}

**{术语2}**:
{定义}
_Avoid_: {避免使用的同义词}

## 关系

- 一个 **{术语A}** 产生一个或多个 **{术语B}**
- 一个 **{术语C}** 属于一个 **{术语A}**

## 示例对话

> **Dev:** "当 **{术语A}** 发生时，我们需要做什么？"
>
> **领域专家:** "{回答}"

## 已澄清的歧义

- "account" 曾被混用表示 **{术语A}** 和 **{术语B}** —— 已澄清：这是两个不同的概念。
```

## 填写规则

### 定义格式

- **简洁**：一句话，定义"是什么"，不是"做什么"
- **避免同义词**：明确列出不要用的词
- **使用领域术语**：用项目自己的词汇

### 关系格式

- 使用粗体术语名：`**Order**`
- 表达基数：`一个`、`多个`、`零个或多个`
- 因果关系：`产生`、`属于`、`依赖`

### 示例对话

- 用 Dev 和领域专家的对话展示术语如何使用
- 展示术语之间的边界
- 不是测试场景，是真实对话

### 歧义记录

当发现术语被混用时：
- 记录原始混用情况
- 说明澄清后的定义
- 明确哪些是不同概念

## 单上下文 vs 多上下文

### 单上下文（大多数项目）

一个 `CONTEXT.md` 文件。

### 多上下文

根目录的 `CONTEXT-MAP.md` 列出各上下文：

```markdown
# Context Map

## 上下文

- [Ordering](./src/ordering/CONTEXT.md) — 接收和跟踪客户订单
- [Billing](./src/billing/CONTEXT.md) — 生成发票和处理支付
- [Fulfillment](./src/fulfillment/CONTEXT.md) — 管理仓库拣货和发货

## 关系

- **Ordering → Fulfillment**: Ordering 发出 `OrderPlaced` 事件；Fulfillment 消费它们开始拣货
- **Fulfillment → Billing**: Fulfillment 发出 `ShipmentDispatched` 事件；Billing 消费它们生成发票
- **Ordering ↔ Billing**: 共享 `CustomerId` 和 `Money` 类型
```

## 惰性创建

- 如果 `CONTEXT.md` 不存在，在第一次术语澄清时创建
- 如果 `CONTEXT.md` 已存在，在新的术语澄清时更新
- 不要添加通用编程概念（超时、错误类型、工具模式）
- 只添加项目特有的领域概念

## 示例

```markdown
# 订单系统

处理客户订单的全生命周期。

## 语言

**Order**:
客户提交的购买请求，包含一个或多个商品。
_Avoid_: 交易、购买

**OrderItem**:
订单中的单个商品，包含商品信息和数量。
_Avoid_: 商品条目、line item

**Customer**:
下单的个人或组织。
_Avoid_: 买家、客户端、账户

**Fulfillment**:
将订单商品配送给客户的过程。
_Avoid_: 发货、配送

## 关系

- 一个 **Customer** 可以有多个 **Order**
- 一个 **Order** 包含一个或多个 **OrderItem**
- 一个 **Order** 产生零个或一个 **Fulfillment**（取消订单不产生）

## 示例对话

> **Dev:** "当一个 **Customer** 下了一个 **Order**，我们什么时候创建 **Fulfillment**？"
>
> **领域专家:** "只有当订单付款完成后才会创建 **Fulfillment**。"

## 已澄清的歧义

- "account" 曾被混用表示 **Customer** 和 **User** —— 已澄清：Customer 是下单实体，User 是登录账户，一个 Customer 可以有多个 User。
```
