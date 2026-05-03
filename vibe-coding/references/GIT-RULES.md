# Git 分支规则

## 分支策略

**重要：** 所有开发代码只能提交到 `develop` 分支，禁止直接提交到 `main` 分支。

| 操作 | 目标分支 | 说明 |
|------|----------|------|
| 日常开发提交 | `develop` | 阶段1-4 的所有提交都提交到 develop |
| 归档完成 | `develop` | 归档前的最终提交提交到 develop |
| 合并到 main | PR | 通过 PR 将 develop 合并到 main |

## 提交时机

- 每个大阶段结束后提交一次
- 每个子任务完成时提交一次
- 验证通过后提交一次

## 提交信息格式

```
feat/task-<序号>: <任务描述>
```

示例：
```
feat/task-01: 实现用户登录功能
feat/task-02: 添加用户注册验证
fix/task-03: 修复密码重置bug
```

## 标签格式

```
v<version>/<变更名称>
```

示例：`v1.0/add-dark-mode`

## PR 创建

归档时必须创建 Pull Request 将 `develop` 分支合并到 `main` 分支。
