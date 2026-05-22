# Coding Patterns — 常见问题模式

本文件记录 coding-skills 在执行过程中发现的常见问题模式，供后续改进参考。

## 安全相关

### 安全凭证泄露
- 关键词: api_key, API_KEY, apikey, secret, token, 密码, password
- 建议: 使用环境变量或 secrets manager，禁止硬编码

### 安全注入风险
- 关键词: exec(), eval(), os.system(), subprocess with shell=True
- 建议: 替换为安全的 API 调用方式

### 高危操作
- 关键词: chmod 777, rm -rf, sudo
- 建议: 评估是否真正需要，如需要则添加确认机制

## 指令理解

### 指令理解偏差
- 关键词: 指令, prompt, 提示词, 推理错误, 误解, 角色, system
- 建议: 优化 SKILL.md 中的指令描述，增加结构化示例

## 工具相关

### 工具缺失
- 关键词: 未找到工具, file not found, module not found, 找不到, scripts/
- 建议: 使用相对路径，检查文件是否存在

### 工具行为错误
- 关键词: 执行失败, runtime error, 行为异常, 不符合预期
- 建议: 检查工具实现的逻辑是否与意图一致

## 上下文管理

### 上下文溢出
- 关键词: context, token, overflow, 溢出, 超出限制, truncated
- 建议: 增加分块策略，限制单次处理的代码行数

## 知识管理

### 重复犯相同错误
- 建议: 在本文件中记录该错误模式作为 anti-pattern

### 知识缺失
- 建议: 在 memory/ 下补充对应技术文档
