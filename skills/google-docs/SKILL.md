---
name: google-docs
description: Create, read, edit, and format Google Docs documents using the Google Docs API. Use when the user mentions Google Docs, wants to create a document, edit content, apply formatting, or work with document URLs.
version: "1.0.0"
---

# Google Docs
allowed-tools: *

## Purpose & Output

Create, read, edit, and format Google Docs documents using the Google Docs API. This skill covers:

- Creating new documents
- Reading document content
- Inserting, updating, and deleting text
- Applying text formatting (bold, italic, headings, colors)
- Creating and updating tables
- Adding comments
- Exporting documents

## Prerequisites

- Service account JSON file with: `client_email`, `private_key`, `project_id`
- Share the document with the service account email (Editor permission)
- Install packages: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

## Authentication

```python
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

with open("credentials.json", "r") as f:
    creds_info = json.load(f)

credentials = Credentials.from_service_account_info(
    creds_info,
    scopes=['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
)

docs_service = build('docs', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
```

## Common Operations

### Create Document

```python
doc = docs_service.documents().create(
    body={"title": "Document Title"}
).execute()

document_id = doc["documentId"]
print(f"Created: https://docs.google.com/document/d/{document_id}/edit")
```

### Read Document

```python
# Get full document
doc = docs_service.documents().get(documentId=document_id).execute()

# Access content
body = doc["body"]
for element in body.get("content", []):
    if "paragraph" in element:
        for run in element["paragraph"].get("elements", []):
            if "textRun" in run:
                print(run["textRun"]["content"])
```

### Insert Text

```python
# Append to end
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": "Hello World\n"
                }
            }
        ]
    }
).execute()

# Insert at specific index
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "insertText": {
                    "location": {"index": 100},
                    "text": "Inserted text"
                }
            }
        ]
    }
).execute()
```

### Update Text

```python
# Replace specific text
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "replaceAllText": {
                    "containsText": {"text": "old text", "matchCase": True},
                    "replaceText": "new text"
                }
            }
        ]
    }
).execute()
```

### Delete Content

```python
# Delete by range
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "deleteContentRange": {
                    "range": {
                        "startIndex": 50,
                        "endIndex": 100
                    }
                }
            }
        ]
    }
).execute()
```

## Text Formatting

### Basic Formatting

```python
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "updateTextStyle": {
                    "range": {"startIndex": 1, "endIndex": 20},
                    "textStyle": {
                        "bold": True,
                        "italic": False,
                        "underline": False,
                        "fontSize": {"magnitude": 14, "unit": "PT"},
                        "foregroundColor": {
                            "color": {"rgbColor": {"red": 0.0, "green": 0.0, "blue": 0.0}}
                        }
                    },
                    "fields": "bold,italic,underline,fontSize,foregroundColor"
                }
            }
        ]
    }
).execute()
```

### Headings

```python
# Apply heading style
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": 1, "endIndex": 50},
                    "paragraphStyle": {
                        "namedStyleType": "HEADING_1",
                        "spaceAbove": {"magnitude": 24, "unit": "PT"},
                        "spaceBelow": {"magnitude": 12, "unit": "PT"}
                    },
                    "fields": "namedStyleType,spaceAbove,spaceBelow"
                }
            }
        ]
    }
).execute()
```

### Named Styles

| Style | Description |
|-------|-------------|
| `NORMAL_TEXT` | Body text (default) |
| `HEADING_1` | Heading 1 |
| `HEADING_2` | Heading 2 |
| `HEADING_3` | Heading 3 |
| `TITLE` | Document title |
| `SUBTITLE` | Subtitle |

### Alignment

```python
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": 1, "endIndex": 100},
                    "paragraphStyle": {
                        "alignment": "CENTER"  # or "LEFT", "RIGHT", "JUSTIFIED"
                    },
                    "fields": "alignment"
                }
            }
        ]
    }
).execute()
```

## Tables

### Create Table

```python
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "insertTable": {
                    "location": {"index": 1},
                    "rows": 3,
                    "columns": 3
                }
            }
        ]
    }
).execute()
```

### Insert Table Cell Content

```python
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "insertText": {
                    "location": {"index": 5},  # Inside table cell
                    "text": "Cell content"
                }
            }
        ]
    }
).execute()
```

## Comments

### Add Comment

```python
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "createComment": {
                    "location": {
                        "range": {"startIndex": 10, "endIndex": 30}
                    },
                    "content": "This needs review"
                }
            }
        ]
    }
).execute()
```

### List Comments

```python
comments = docs_service.documents().comments().list(
    documentId=document_id
).execute()

for comment in comments.get("comments", []):
    print(f"{comment['author']['displayName']}: {comment['content']}")
```

## Document Structure

### Get Document Index

The Google Docs API uses an index system for content locations:

```python
def find_text_index(doc, search_text):
    """Find the start index of text in document"""
    body = doc["body"]
    content = body.get("content", [])
    
    for element in content:
        if "paragraph" in element:
            for run in element["paragraph"].get("elements", []):
                if "textRun" in run:
                    text = run["textRun"]["content"]
                    if search_text in text:
                        return run["startIndex"]
    return None
```

### Insert Break (Page/Column)

```python
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "insertText": {
                    "location": {"index": 100},
                    "text": "\n"
                }
            },
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": 100, "endIndex": 101},
                    "paragraphStyle": {"pageBreakBefore": True},
                    "fields": "pageBreakBefore"
                }
            }
        ]
    }
).execute()
```

## Lists

### Create Bulleted List

```python
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "createParagraphBullets": {
                    "range": {"startIndex": 50, "endIndex": 150},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                }
            }
        ]
    }
).execute()
```

### Create Numbered List

```python
docs_service.documents().batchUpdate(
    documentId=document_id,
    body={
        "requests": [
            {
                "createParagraphBullets": {
                    "range": {"startIndex": 50, "endIndex": 150},
                    "bulletPreset": "NUMBERED_DECIMAL_NESTED"
                }
            }
        ]
    }
).execute()
```

## Document Operations

### Copy Document

```python
copied = drive_service.files().copy(
    fileId=document_id,
    body={"name": "Copy of Document"}
).execute()

new_id = copied["id"]
```

### Move to Folder

```python
drive_service.files().update(
    fileId=document_id,
    addParents="folder_id",
    removeParents="previous_folder_id",
    fields="id, parents"
).execute()
```

### Share Document

```python
# Share with specific user
drive_service.permissions().create(
    fileId=document_id,
    body={
        "role": "writer",  # or "reader", "commenter"
        "type": "user",
        "emailAddress": "user@example.com"
    }
).execute()

# Make public
drive_service.permissions().create(
    fileId=document_id,
    body={
        "role": "reader",
        "type": "anyone"
    }
).execute()
```

## Export Document

```python
# Export as PDF
pdf = drive_service.files().export(
    fileId=document_id,
    mimeType="application/pdf"
).execute()

with open("document.pdf", "wb") as f:
    f.write(pdf)

# Export as DOCX
docx = drive_service.files().export(
    fileId=document_id,
    mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
).execute()

with open("document.docx", "wb") as f:
    f.write(docx)
```

## URL Operations

### Get Document ID from URL

```python
import re

def get_document_id(url):
    """Extract document ID from Google Docs URL"""
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not match:
        raise ValueError("Invalid Google Docs URL")
    return match.group(1)

url = "https://docs.google.com/document/d/{id}/edit"
document_id = get_document_id(url)
```

## Document Design

### Typography Best Practices

- Use named styles for consistency (HEADING_1, HEADING_2, etc.)
- Maintain hierarchy: Title > Heading 1 > Heading 2 > Body
- Use appropriate font sizes: Title (24-32pt), Headings (16-24pt), Body (11-14pt)

### Color Palette

```python
# Common colors (RGB 0-1 scale)
colors = {
    "black": {"red": 0, "green": 0, "blue": 0},
    "white": {"red": 1, "green": 1, "blue": 1},
    "red": {"red": 1, "green": 0, "blue": 0},
    "blue": {"red": 0, "green": 0, "blue": 1},
    "gray": {"red": 0.5, "green": 0.5, "blue": 0.5}
}
```

## Code Style Guidelines

- Batch multiple requests when possible
- Use meaningful variable names for document IDs
- Handle index calculations carefully
- Log document URLs for user reference
- Validate document access before operations

