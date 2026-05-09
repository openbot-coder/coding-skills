# Development Workflow Skill Guide

## Overview

Dev workflow skills automate development tasks and enforce best practices throughout the software development lifecycle.

## When to Use

- Automating Git workflows
- Project scaffolding
- Code generation
- Build and deployment automation
- Testing and quality checks

## Directory Structure

```
dev-workflow-skill/
├── SKILL.md
├── scripts/
│   ├── workflow.py         # Workflow orchestration
│   └── helpers.py          # Utility functions
├── references/
│   └── standards.md        # Coding standards
└── assets/
    └── templates/          # Project templates
```

## Frontmatter Template

```yaml
---
name: git-workflow
description: "Automate Git workflows including branching, merging, and pull request management. Use when managing Git repositories or implementing CI/CD pipelines."
version: 1.0.0
license: MIT
compatibility: Requires git CLI
metadata:
  author: dev-team
  category: development
  tags: [git, workflow, automation]
---
```

## Key Components

### 1. Workflow Orchestration

```python
# scripts/workflow.py
import subprocess

class GitWorkflow:
    def create_feature_branch(self, name):
        subprocess.run(["git", "checkout", "-b", f"feature/{name}"])
    
    def commit_with_message(self, message):
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", message])
    
    def push_to_remote(self, branch=None):
        branch = branch or self._get_current_branch()
        subprocess.run(["git", "push", "origin", branch])
```

### 2. Workflow Templates

- **Feature Branch**: Create → Develop → PR → Review → Merge
- **Release Flow**: Branch → Test → Tag → Deploy
- **Hotfix**: Create → Fix → Merge → Deploy

### 3. Automation Hooks

- Pre-commit hooks
- Commit message validation
- Branch naming conventions
- CI/CD integration

## Example Usage

```markdown
# Git Workflow

## Overview

This skill automates common Git workflows and enforces best practices.

## Workflows

### Feature Development

1. Create feature branch: `feature/feature-name`
2. Commit changes with conventional messages
3. Push to remote
4. Create pull request
5. Review and merge

### Release Process

1. Create release branch: `release/v1.0.0`
2. Run tests
3. Tag version
4. Deploy to production

## Usage

```python
from scripts.workflow import GitWorkflow

workflow = GitWorkflow()
workflow.create_feature_branch("new-feature")
workflow.commit_with_message("feat: add new feature")
workflow.push_to_remote()
```

## Best Practices

1. **Branch Naming**: Use consistent conventions (feature/, bugfix/, release/)
2. **Commit Messages**: Follow conventional commits
3. **Code Reviews**: Require PR reviews before merging
4. **Testing**: Run tests before merging
5. **Documentation**: Update docs with changes

## Branching Strategy

| Branch Type | Pattern | Purpose |
|-------------|---------|---------|
| main | `main` | Production-ready code |
| develop | `develop` | Integration branch |
| feature | `feature/*` | New features |
| bugfix | `bugfix/*` | Bug fixes |
| release | `release/*` | Release preparation |
| hotfix | `hotfix/*` | Urgent fixes |
