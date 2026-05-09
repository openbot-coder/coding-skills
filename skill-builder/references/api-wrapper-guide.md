# API Wrapper Skill Guide

## Overview

API wrapper skills provide structured interfaces for interacting with external APIs. They encapsulate authentication, request handling, and response parsing to simplify API interactions.

## When to Use

- Interacting with RESTful APIs
- Wrapping third-party services (GitHub, Stripe, Slack, etc.)
- Creating reusable API clients
- Standardizing API access patterns

## Directory Structure

```
api-wrapper-skill/
├── SKILL.md
├── scripts/
│   └── api_client.py      # API client implementation
├── references/
│   └── api_docs.md        # API documentation
└── assets/
    └── examples/          # Example API calls
```

## Frontmatter Template

```yaml
---
name: service-api-wrapper
description: "Interact with Service API for resource management. Use when working with Service resources, endpoints, or data operations."
version: 1.0.0
license: MIT
compatibility: Requires network access and API credentials
metadata:
  author: dev-team
  category: api
  tags: [api, service, integration]
---
```

## Key Components

### 1. API Client Class

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

### 2. Error Handling

- Implement retries for transient errors
- Handle rate limiting
- Validate API responses
- Log errors with context

### 3. Authentication

- API keys
- OAuth 2.0
- Bearer tokens
- Environment variables for credentials

## Example Usage

```markdown
# Service API Wrapper

## Overview

This skill provides functions to interact with Service API.

## Available Functions

- `get_resource(resource_id)` - Get resource by ID
- `create_resource(data)` - Create new resource
- `update_resource(resource_id, data)` - Update resource
- `delete_resource(resource_id)` - Delete resource

## Usage

```python
from scripts.api_client import APIClient

# Initialize client
client = APIClient(
    base_url="https://api.service.com/v1",
    api_key=os.environ.get("SERVICE_API_KEY")
)

# Get resource
resource = client.get_resource("abc123")
```

## Best Practices

1. **Credential Management**: Store credentials in environment variables
2. **Rate Limiting**: Implement backoff strategies
3. **Error Handling**: Provide meaningful error messages
4. **Documentation**: Include API endpoint references
5. **Testing**: Mock API calls for unit tests
