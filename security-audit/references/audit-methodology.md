# 安全审计方法论

> 本文档描述系统性安全审计的步骤和方法

---

## 审计流程概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      阶段1：情报收集                              │
│  理解架构 → 识别入口点 → 定位信任边界 → 追踪数据流                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      阶段2：攻击面枚举                            │
│  认证漏洞 → 注入向量 → 外部交互 → 敏感数据                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      阶段3：利用验证                              │
│  路径追踪 → PoC 开发 → 严重度评估                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      阶段4：报告生成                              │
│  证据整理 → 分级输出 → 修复建议                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 阶段1：情报收集

### 1.1 架构理解

**关键问题**：
1. 应用类型？（Web API、CLI、桌面应用、微服务）
2. 技术栈？（语言、框架、数据库、中间件）
3. 部署模式？（本地、云、混合）
4. 信任边界？（内网/外网、API 消费者）

**信息收集命令**：

```bash
# 项目结构分析
find . -type f -name "*.py" -o -name "*.js" -o -name "*.java" | head -50

# 依赖分析
cat package.json  # Node.js
cat requirements.txt  # Python
cat pom.xml  # Java

# 配置文件
find . -name "*.env*" -o -name "config*" -o -name "application*.yml"
```

### 1.2 入口点识别

| 入口类型 | 检查位置 |
|----------|----------|
| HTTP API | 路由定义、中间件配置 |
| GraphQL | schema 定义、resolver |
| CLI | 命令行参数解析 |
| WebSocket | 连接处理、消息路由 |
| 文件上传 | 处理端点、存储路径 |
| 定时任务 | Cron 配置、任务调度器 |

**识别命令**：

```bash
# API 路由
grep -rn "router\|@app\|@router\|@api\|@route" --include="*.py" --include="*.js"

# 入口文件
ls -la index.js main.py main.go App.java

# 环境变量配置
grep -rn "process.env\|os.environ\|getenv" --include="*.py" --include="*.js"
```

### 1.3 信任边界定位

**常见信任边界**：
- 防火墙/DMZ
- API 网关
- 认证中间件
- 防火墙规则
- 进程隔离

**检查清单**：
- [ ] 哪些端点需要认证？
- [ ] 哪些端点标记为公开？
- [ ] 认证如何实现？（JWT/Session/OAuth）
- [ ] 是否有测试/开发端点暴露？

### 1.4 数据流追踪

```
用户输入点                    数据存储点
    ↓                              ↑
HTTP 参数 ──→ 验证层 ──→ 业务逻辑 ──→ ORM/DAL
    ↓                              ↑
请求头 ────→ 中间件 ──→ 缓存层 ────→ 数据库
    ↓                              ↑
文件上传 ──→ 存储处理 ──→ CDN ──────→ OSS/S3
```

**追踪技术**：
1. 从用户输入开始，向后追踪数据处理
2. 从数据库访问点开始，向前追踪数据来源
3. 标记所有数据转换和校验点

---

## 阶段2：攻击面枚举

### 2.1 认证与访问控制审计

#### 会话管理

| 检查项 | 检测命令 | 危险阈值 |
|--------|----------|----------|
| 会话 ID 生成 | `grep -rn "random\|uuid" session` | Math.random() |
| 会话存储 | `grep -rn "session" config` | 无过期设置 |
| 会话固定 | 代码审查 | 登录后未刷新 ID |

#### 密码处理

| 检查项 | 检测命令 | 危险阈值 |
|--------|----------|----------|
| 密码哈希 | `grep -rn "hash\|password" --include="*.py"` | md5/sha1 |
| 密码强度 | 代码审查 | 无复杂度要求 |
| 凭证传输 | `grep -rn "http://"` | 非 HTTPS |

#### 权限控制

| 检查项 | 检测命令 | 危险阈值 |
|--------|----------|----------|
| 路由权限 | `grep -rn "admin\|/api/.*"` | 缺少中间件 |
| 数据权限 | 代码审查 | 缺少 owner 校验 |
| 功能权限 | 代码审查 | 基于白名单而非黑名单 |

### 2.2 注入漏洞审计

#### SQL 注入

**检测顺序**：
1. 查找原始 SQL 执行位置
2. 追踪用户输入到 SQL 的路径
3. 验证是否存在参数化查询

```python
# 危险模式识别
dangerous = [
    "execute(",
    "query(",
    "raw(",
    ".filter(",
]

# 参数化检查
safe_patterns = [
    "execute('%s'",
    "execute(?, [",
    "db.query({text:",
]
```

**测试用例**：
```sql
' OR '1'='1
" OR "1"="1
' UNION SELECT NULL--
1; DROP TABLE users--
```

#### 命令注入

**检测模式**：
```javascript
dangerous_functions = [
    'exec(', 'execSync(',
    'eval(',
    'spawn(', 'spawnSync(',
    'child_process.exec',
    'child_process.execSync',
]

# Python
dangerous = [
    'os.system(',
    'os.popen(',
    'subprocess.call(',
    'subprocess.run(',
    'eval(',
    'exec(',
]
```

#### 模板注入

**检测步骤**：
1. 识别模板引擎（Jinja2、Handlebars、EJS）
2. 查找 `render()` 调用
3. 检查用户输入是否进入模板

```python
# Jinja2 危险模式
template.render(user_input=user_input)  # 直接渲染用户输入

# 安全模式
template.render(items=safe_items, total=calculate(user_input))
```

### 2.3 敏感数据审计

#### 凭证泄露

```bash
# Git 历史搜索
git log -p --all -S "password" -- "*.py" "*.js"
git log -p --all -S "api_key" -- "*.py" "*.js"
git log -p --all -S "secret" -- "*.py" "*.js"

# 当前代码搜索
grep -rEn "(password|passwd|pwd|secret|apikey|token)\s*=\s*['\"]" --include="*.py" --include="*.js"

# 配置文件
find . -name "*.env" -o -name ".env*" -o -name "*.example"
```

#### 日志泄露

```javascript
// 危险模式
console.log(req.body.password)
console.log(req.headers.authorization)
logger.info('Token:', token)

// 安全模式
logger.info('Request from user:', userId)
```

### 2.4 外部交互审计

#### SSRF 检测

```javascript
// 危险 - URL 来自用户
fetch(url)  // url 用户可控
axios.get(url)

// 安全 - URL 限制
const allowed = ['https://api.internal.com/'];
if (!isAllowed(url)) throw Error('Forbidden');
```

#### Webhook 安全

| 检查项 | 要求 |
|--------|------|
| 签名验证 | 必须校验 HMAC |
| 时间戳 | 请求 5 分钟内有效 |
| 幂等性 | 防止重放攻击 |

---

## 阶段3：利用验证

### 3.1 利用路径追踪模板

```
┌──────────────────────────────────────────────────────────────────┐
│ 攻击者可控输入                                                    │
│   ↓                                                              │
│ [入口点: HTTP 参数/Header/文件]                                   │
│   ↓                                                              │
│ [数据传播路径]                                                    │
│   ↓                                                              │
│ [漏洞触发点]                                                      │
│   ↓                                                              │
│ [影响结果]                                                        │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 严重度评估

#### CVSS 3.1 计算因子

| 向量 | 选项 | 影响 |
|------|------|------|
| Attack Vector | Network/Adjacent/Local/Physical | 影响范围 |
| Attack Complexity | Low/High | 利用难度 |
| Privileges Required | None/Low/High | 所需权限 |
| User Interaction | None/Required | 是否需要用户 |
| Scope | Unchanged/Changed | 是否越界 |

#### 简化评估表

| 影响 | 所需权限 | 严重度 |
|------|----------|--------|
| RCE | 无 | Critical |
| 数据完全泄露 | 无 | Critical |
| RCE | 认证用户 | High |
| 数据部分泄露 | 无 | High |
| 数据部分泄露 | 认证用户 | Medium |

### 3.3 PoC 要求

对于每个报告的漏洞，必须提供：

1. **利用条件**：需要哪些前置条件？
2. **利用步骤**：完整的攻击流程
3. **可验证性**：他人能否复现？

**PoC 模板**：
```markdown
### PoC

**环境要求**：
- 目标版本：v1.2.3
- 网络可达性：外网可访问

**利用步骤**：
1. 发送请求：
```bash
curl -X POST https://target.com/api/endpoint \
  -d 'param=value'
```

2. 观察结果：
- 响应内容
- 副作用（数据变更）

3. 验证影响：
- 确认数据泄露
- 或确认代码执行
```

---

## 阶段4：报告生成

### 4.1 报告结构

```markdown
# 安全审计报告

## 执行摘要
- 审计范围：
- 审计时间：
- 发现数量：
- 严重度分布：

## 发现详情

### [严重度] 漏洞名称

**位置**：`src/path/file.ext:行号`
**CWE**：CWE-XXX
**CVSS**：X.X

#### 描述
[漏洞详细说明]

#### 攻击者画像
[谁可以利用此漏洞]

#### 输入向量
[具体可控输入]

#### 代码路径
```
[文件:行号] 输入接收
[文件:行号] 处理逻辑
[文件:行号] 漏洞点 ←
```

#### 影响评估
[具体可量化影响]

#### 修复建议
```[语言]
// 建议的修复代码
```

#### PoC
[利用证明]
```

### 4.2 无漏洞报告

```markdown
## 审计结论

**审计范围**：[项目/组件]
**审计时间**：[日期]
**审计方法**：静态分析 + 代码审查

### 结果

审计完成——未发现中等或更高严重度的已确认漏洞。

### 说明

本次审计覆盖以下攻击面：
- [ ] 认证与会话管理
- [ ] 注入向量（SQL、命令、模板）
- [ ] 敏感数据处理
- [ ] 外部交互安全
- [ ] 访问控制

虽然未发现可利用的漏洞，建议持续关注：
- 依赖项安全更新
- 新功能的安全评审
- 渗透测试

---
**审计人**：[签名]
**日期**：[日期]
```

---

## 附录：审计工具清单

### 静态分析

| 工具 | 语言 | 用途 |
|------|------|------|
| Semgrep | 多语言 | 代码模式匹配 |
| Bandit | Python | Python 安全分析 |
| ESLint + security | JavaScript | JS 安全规则 |
| SonarQube | 多语言 | 综合代码质量 |

### 依赖扫描

| 工具 | 用途 |
|------|------|
| npm audit | Node.js 依赖 |
| pip-audit | Python 依赖 |
| Snyk | 多语言依赖 |

### 秘钥检测

| 工具 | 用途 |
|------|------|
| GitLeaks | Git 历史扫描 |
| TruffleHog | 秘钥检测 |
| SecretScanner | 容器镜像扫描 |
