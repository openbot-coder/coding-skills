# Evolution

> AI 自驱动：每次迭代后收集证据、更新 manifest、决策是否继续

## 何时使用

- 每次变更完成（`progress.md` 更新后）
- 需要评估是否继续迭代
- 需要更新项目知识图谱

## 前置检查

1. 读取 `progress.md` 当前状态
2. 读取 `evidence/` 目录（如存在）
3. 读取 `changelog.md` 最新记录

## 执行流程

### Step 1：收集证据

证据类型：

| 类型 | 内容 | 保存位置 |
|------|------|----------|
| 测试报告 | pytest 输出 | `evidence/{change}/test-report.txt` |
| 覆盖率报告 | coverage 输出 | `evidence/{change}/coverage.txt` |
| 性能数据 | benchmark 结果 | `evidence/{change}/benchmark.txt` |
| 代码质量 | lint 输出 | `evidence/{change}/lint.txt` |

```bash
# 自动收集证据
pytest -v --tb=short > evidence/{change}/test-report.txt 2>&1
coverage report > evidence/{change}/coverage.txt 2>&1
```

### Step 2：生成证据报告

```markdown
## Evidence Report: {变更名称}

**时间**: {timestamp}  
**状态**: {成功/失败/部分成功}

### 测试结果
- 总测试数: 47
- 通过: 46
- 失败: 1
- 覆盖率: 98%

### 变更规模
- 新增行数: 180
- 修改行数: 45
- 删除行数: 12

### 决策
- 继续: ☐
- 暂停: ☐
- 回滚: ☐
```

### Step 3：更新 Change Manifest

`manifest.md` 记录所有变更历史：

```markdown
# Change Manifest

## 变更历史

| 日期 | 变更 | 结果 | 决策 |
|------|------|------|------|
| 2026-05-23 | 添加暗色模式 | 47测试/46通过 | 继续 |
| 2026-05-22 | 重构会话管理 | 32测试/32通过 | 继续 |
```

### Step 4：迭代决策

基于证据做出决策：

| 证据 | 决策 | 动作 |
|------|------|------|
| 测试通过率 > 95% | ✅ 继续 | 下一个功能 |
| 测试通过率 80-95% | ⚠️ 暂停修复 | 修复已知问题 |
| 测试通过率 < 80% | ❌ 回滚 | 恢复到上一个稳定版本 |
| 覆盖率下降 | ⚠️ 暂停 | 优先提升覆盖率 |

### Step 5：更新项目上下文

如果决策是继续，更新 `design.md`：

```markdown
## 已完成功能
- [x] 暗色模式 (v1.0.0, 2026-05-23)
- [x] 会话持久化 (v0.9.0, 2026-05-22)

## 待实现功能
- [ ] 多语言支持
- [ ] 主题自定义
```

## 证据持久化

证据目录结构：

```
evidence/
├── {change-name}/
│   ├── test-report.txt    # pytest 输出
│   ├── coverage.txt       # coverage 报告
│   ├── benchmark.txt     # 性能基准
│   └── decision.md       # 决策记录
└── manifest.md           # 变更总表
```

## Git 提交

每次迭代后提交证据：

```bash
git add evidence/
git commit -m "docs: 记录 {变更名} 迭代证据"
git push origin develop
```

## 反模式

- ❌ 不收集证据就声称"完成"
- ❌ 证据与决策不一致
- ❌ 不更新 manifest
- ❌ 忽视性能数据
- ❌ 不更新 design.md

## 触发条件

以下任一情况触发：

1. 每次变更 `progress.md` 状态更新后
2. `progress.md` 中所有任务 `✅ 已完成`
3. 用户要求评估项目状态
