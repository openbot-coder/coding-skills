# Document Processor Skill Guide

## Overview

Document processor skills handle specific file formats and provide operations like extraction, transformation, and analysis.

## When to Use

- Processing PDF documents
- Analyzing Excel spreadsheets
- Parsing CSV files
- Converting document formats
- Extracting text and metadata

## Directory Structure

```
document-processor-skill/
├── SKILL.md
├── scripts/
│   ├── parser.py           # Document parsing logic
│   └── extractor.py        # Data extraction
├── references/
│   └── format_spec.md      # Format specifications
└── assets/
    └── templates/          # Output templates
```

## Frontmatter Template

```yaml
---
name: pdf-processor
description: "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF documents or document extraction tasks."
version: 1.0.0
license: MIT
compatibility: Requires PyPDF2 or pdfplumber
metadata:
  author: dev-team
  category: document-processing
  tags: [pdf, extraction, documents]
---
```

## Key Components

### 1. Document Parser

```python
# scripts/parser.py
import pdfplumber

class PDFProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def extract_text(self):
        with pdfplumber.open(self.file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    def extract_tables(self):
        with pdfplumber.open(self.file_path) as pdf:
            tables = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                tables.extend(page_tables)
        return tables
```

### 2. Output Formats

- Text extraction
- Table extraction (CSV, JSON)
- Metadata extraction
- Image extraction
- Document conversion

### 3. Processing Pipeline

1. **Input**: Accept file path or content
2. **Parsing**: Extract structured data
3. **Transformation**: Convert to desired format
4. **Output**: Return or save results

## Example Usage

```markdown
# PDF Processor

## Overview

This skill extracts text and tables from PDF documents.

## Features

- Text extraction with layout preservation
- Table extraction as CSV or JSON
- Metadata extraction (author, date, pages)
- Form field extraction

## Usage

```python
from scripts.parser import PDFProcessor

# Process PDF
processor = PDFProcessor("document.pdf")

# Extract text
text = processor.extract_text()

# Extract tables
tables = processor.extract_tables()
```

## Best Practices

1. **Memory Management**: Handle large files efficiently
2. **Error Handling**: Validate file formats before processing
3. **Output Options**: Support multiple output formats
4. **Performance**: Optimize for large documents
5. **Format Support**: Handle different PDF versions

## Supported Formats

- PDF (via pdfplumber, PyPDF2)
- DOCX (via python-docx)
- XLSX (via pandas, openpyxl)
- CSV (via csv module)
- JSON (built-in)
