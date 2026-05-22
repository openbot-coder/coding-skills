# Security Audit Checklist

## 凭证安全

- [ ] 禁止在脚本中硬编码密码、API Key、Token
- [ ] 必须使用环境变量: `os.environ.get("API_KEY")`
- [ ] 或使用 secrets manager

## 代码注入

- [ ] 禁止使用 `exec()` / `eval()` 处理用户输入
- [ ] 使用 `subprocess.run()` 替代 `os.system()`
- [ ] `subprocess.run(shell=False)` 防止 shell 注入
- [ ] 使用 `ast.literal_eval()` 替代 `eval()` 处理数据解析

## 文件操作

- [ ] 避免 `chmod 777`，使用 `chmod 755` 或更严格
- [ ] `rm -rf` 前添加确认提示
- [ ] 评估 `sudo` 是否真正需要

## 输入验证

- [ ] 对所有外部输入进行验证
- [ ] 防止路径遍历攻击 (`../`)
- [ ] 限制文件操作在允许的目录范围内
