# API 包装器技能指南

> **设计模式：** 🛠 Tool Wrapper — 让 Agent 瞬间成为任意库的专家

## 概述

API 包装器技能为与外部 API 交互提供结构化接口。它们封装了认证、请求处理和响应解析，以简化 API 交互。

## 使用场景

- 与 RESTful API 交互
- 包装第三方服务（GitHub、Stripe、Slack 等）
- 创建可重用的 API 客户端
- 标准化 API 访问模式

## 目录结构

```
api-wrapper-skill/
├── SKILL.md
├── scripts/
│   └── api_client.py      # API 客户端实现
├── references/
│   └── api_docs.md        # API 文档
└── assets/
    └── examples/          # API 调用示例
```

## Frontmatter 模板

```yaml
---
name: service-api-wrapper
description: "与服务 API 交互以进行资源管理。在处理服务资源、端点或数据操作时使用。"
version: 1.0.0
license: MIT
compatibility: 需要网络访问和 API 凭证
metadata:
  author: dev-team
  category: api
  tags: [api, service, integration]
---
```

## 核心组件

### 1. API 客户端类

```python
# scripts/api_client.py
import requests

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def get_resource(self, resource_id):
        response = requests.get(
            f"{self.base_url}/resources/{resource_id}",
            headers=self.headers
        )
        return response.json()
    
    def create_resource(self, data):
        response = requests.post(
            f"{self.base_url}/resources",
            headers=self.headers,
            json=data
        )
        return response.json()
```

### 2. 错误处理

- 为瞬时错误实现重试机制
- 处理速率限制
- 验证 API 响应
- 记录带有上下文的错误

### 3. 认证方式

- API 密钥
- OAuth 2.0
- Bearer tokens
- 环境变量存储凭证

## 使用示例

```markdown
# 服务 API 包装器

## 概述

此技能提供与服务 API 交互的功能。

## 可用函数

- `get_resource(resource_id)` - 根据 ID 获取资源
- `create_resource(data)` - 创建新资源
- `update_resource(resource_id, data)` - 更新资源
- `delete_resource(resource_id)` - 删除资源

## 使用方法

```python
from scripts.api_client import APIClient

# 初始化客户端
client = APIClient(
    base_url="https://api.service.com/v1",
    api_key=os.environ.get("SERVICE_API_KEY")
)

# 获取资源
resource = client.get_resource("abc123")
```

## 最佳实践

1. **凭证管理**：将凭证存储在环境变量中
2. **速率限制**：实现退避策略
3. **错误处理**：提供有意义的错误消息
4. **文档**：包含 API 端点参考
5. **测试**：为单元测试模拟 API 调用
