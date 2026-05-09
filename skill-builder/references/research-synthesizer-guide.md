# Research Synthesizer Skill Guide

## Overview

Research synthesizer skills gather information from multiple sources, analyze it, and produce structured reports or summaries.

## When to Use

- Competitive analysis
- Literature reviews
- Market research
- Data aggregation
- Information synthesis

## Directory Structure

```
research-synthesizer-skill/
├── SKILL.md
├── scripts/
│   ├── researcher.py       # Research logic
│   └── analyzer.py         # Analysis functions
├── references/
│   └── sources.md          # Source documentation
└── assets/
    └── templates/          # Report templates
```

## Frontmatter Template

```yaml
---
name: competitive-analysis
description: "Perform competitive analysis by gathering and synthesizing information about competitors. Use when researching market trends, competitor products, or industry landscape."
version: 1.0.0
license: MIT
metadata:
  author: dev-team
  category: research
  tags: [analysis, research, competitive]
---
```

## Key Components

### 1. Researcher Class

```python
# scripts/researcher.py
import requests
from bs4 import BeautifulSoup

class Researcher:
    def __init__(self):
        self.sources = []
    
    def add_source(self, url):
        self.sources.append(url)
    
    def fetch_content(self, url):
        response = requests.get(url)
        return response.text
    
    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def synthesize(self):
        findings = []
        for source in self.sources:
            content = self.fetch_content(source)
            text = self.parse_html(content)
            findings.append({"source": source, "content": text})
        return findings
```

### 2. Analysis Techniques

- **Content Extraction**: Extract key information from sources
- **Sentiment Analysis**: Determine sentiment of text
- **Topic Modeling**: Identify main topics
- **Comparison**: Compare multiple sources
- **Summarization**: Generate concise summaries

### 3. Output Formats

- Markdown reports
- JSON data structures
- Visual summaries
- Comparative tables

## Example Usage

```markdown
# Competitive Analysis

## Overview

This skill gathers information about competitors and produces structured analysis reports.

## Research Process

1. **Identify Sources**: List competitor websites, articles, reviews
2. **Gather Information**: Fetch and parse content
3. **Analyze**: Extract key metrics and insights
4. **Synthesize**: Combine findings into report

## Usage

```python
from scripts.researcher import Researcher

researcher = Researcher()
researcher.add_source("https://competitor1.com")
researcher.add_source("https://competitor2.com")

findings = researcher.synthesize()
```

## Best Practices

1. **Source Quality**: Use reputable sources
2. **Diversity**: Gather from multiple perspectives
3. **Citation**: Track sources for reference
4. **Bias Awareness**: Consider source biases
5. **Timeliness**: Use recent information

## Report Structure

```markdown
# Competitive Analysis Report

## Executive Summary

Brief overview of findings...

## Competitors

| Competitor | Strengths | Weaknesses |
|------------|-----------|------------|
| Competitor A | Feature X | Weak UI |
| Competitor B | Low price | Limited features |

## Key Findings

1. Finding 1
2. Finding 2
3. Finding 3

## Recommendations

Based on analysis...
```

## Information Sources

- Company websites
- Industry reports
- News articles
- Customer reviews
- Social media
- Technical documentation
