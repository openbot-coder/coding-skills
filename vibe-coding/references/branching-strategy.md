# Git 分支策略

## 分支结构

### 主分支

| 分支 | 用途 | 保护 |
|------|------|------|
| `main` | 生产就绪代码 | ✅ 受保护，禁止直接提交 |
| `develop` | 集成开发分支 | ✅ 受保护，仅接受 PR |

### 辅助分支

| 分支类型 | 命名模式 | 用途 | 生命周期 |
|----------|----------|------|----------|
| feature | `feature/{name}` | 新功能开发 | 短期 |
| bugfix | `bugfix/{name}` | 错误修复 | 短期 |
| release | `release/{version}` | 发布准备 | 短期 |
| hotfix | `hotfix/{name}` | 紧急修复 | 短期 |

## 分支创建规则

### Feature 分支

**创建来源：** `develop`

**命名规范：**
```
feature/{feature-name}
feature/add-dark-mode
feature/api-integration
```

**用途：**
- 开发新功能
- 实现用户需求
- 每个功能一个分支

### Bugfix 分支

**创建来源：** `develop`

**命名规范：**
```
bugfix/{bug-description}
bugfix/login-error
bugfix/memory-leak
```

**用途：**
- 修复开发中的 bug
- 不影响生产环境

### Release 分支

**创建来源：** `develop`

**命名规范：**
```
release/{version}
release/v1.0.0
release/v2.1.0
```

**用途：**
- 准备发布
- 版本号锁定
- 最终测试

### Hotfix 分支

**创建来源：** `main`

**命名规范：**
```
hotfix/{issue-description}
hotfix/production-crash
hotfix/security-vulnerability
```

**用途：**
- 修复生产环境紧急问题
- 绕过正常流程
- 快速部署

## 分支合并规则

### Feature → Develop

**流程：**
1. 完成功能开发
2. 创建 Pull Request
3. 代码审查
4. 通过后合并到 `develop`
5. 删除 feature 分支

### Develop → Main

**时机：**
- 版本发布时
- 通过 release 分支

**流程：**
1. 从 `develop` 创建 `release/{version}` 分支
2. 在 release 分支上进行最终测试
3. 创建 PR 将 release 合并到 `main`
4. 创建 PR 将 release 合并回 `develop`
5. 删除 release 分支
6. 在 `main` 上创建版本标签

### Hotfix → Main & Develop

**流程：**
1. 从 `main` 创建 `hotfix/{issue}` 分支
2. 修复问题
3. 创建 PR 合并到 `main`
4. 创建 PR 合并到 `develop`
5. 删除 hotfix 分支
6. 在 `main` 上创建版本标签

## 提交规范

### 提交信息格式

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): add login endpoint` |
| `fix` | 修复 bug | `fix(api): handle null response` |
| `docs` | 文档更新 | `docs: update README` |
| `style` | 代码格式 | `style: format code` |
| `refactor` | 重构 | `refactor: simplify logic` |
| `test` | 测试 | `test: add unit tests` |
| `chore` | 杂务 | `chore: update dependencies` |

### 示例

```
feat(user): add profile page

- Add user profile page component
- Implement avatar upload
- Add edit profile functionality

Closes #123
```

## 标签规范

### 版本标签

**格式：**
```
v<major>.<minor>.<patch>
v1.0.0
v2.1.3
```

**创建时机：**
- 合并到 `main` 时
- hotfix 修复后

### 变更标签（可选）

**格式：**
```
v<version>/<change-name>
v1.0/add-dark-mode
```

**创建时机：**
- 归档完成后

## 保护规则

### Main 分支

- ✅ 禁止直接推送
- ✅ 必须通过 PR
- ✅ 需要至少 1 个审查批准
- ✅ 必须通过 CI 检查

### Develop 分支

- ✅ 禁止直接推送
- ✅ 必须通过 PR
- ✅ 需要至少 1 个审查批准
- ✅ 必须通过 CI 检查

### 其他分支

- ❌ 无强制保护
- ⚠️ 建议代码审查

## 工作流示例

### 正常功能开发

```
main ──────────────────────────► main
  │                               ▲
  │                               │ PR
  │                         release/v1.0
  │                               │
develop ◄─── merge ─── feature/add-login ─── create
  │
  ▼
develop
```

### Hotfix 流程

```
main ─── create ─── hotfix/crash ─── merge ─── main
  │                                              │
  │                                              │ merge
  │                                              ▼
develop ◄─────────────────────────────────────── develop
```

## 工具支持

### 自动检查

- pre-commit hooks 检查提交格式
- CI 运行测试
- 代码质量检查

### 推荐工具

- **commitlint**：提交信息格式检查
- **pre-commit**：提交前检查
- **GitHub Actions**：CI/CD
