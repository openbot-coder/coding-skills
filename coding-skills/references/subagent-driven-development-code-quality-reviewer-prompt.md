# 代码质量审查提示模板

在派遣代码质量审查子智能体时使用此模板。

**目的：** 验证实现是否构建良好（干净、经过测试、可维护）

**仅在规格合规审查通过后派遣。**

```
Task 工具 (superpowers:code-reviewer):
  使用 requesting-code-review/code-reviewer.md 中的模板

  WHAT_WAS_IMPLEMENTED: [来自实现者的报告]
  PLAN_OR_REQUIREMENTS: [计划文件] 中的任务 N
  BASE_SHA: [任务前的提交]
  HEAD_SHA: [当前提交]
  DESCRIPTION: [任务摘要]
```

**代码审查者返回：** 优点、问题（严重/重要/次要）、评估
