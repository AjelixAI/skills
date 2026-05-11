---
name: google-slides
description: Create, design, edit, and manipulate Google Slides presentations using the Google Slides API. Use when the user mentions Google Slides, wants to create a presentation, edit slides, or work with presentation URLs.
version: "1.0.0"
---

# Google Slides
allowed-tools: *

## Purpose & Output

Create, design, edit, and manipulate Google Slides presentations using the Google Slides API. This skill covers:

- Creating new presentations
- Adding, deleting, and duplicating slides
- Editing text content and formatting
- Adding shapes, images, and tables
- Applying layout templates
- Working with master slides and themes

## Prerequisites

- Service account JSON file with: `client_email`, `private_key`, `project_id`
- Share the presentation with the service account email (Editor permission)
- Install packages: `pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`

## Authentication

```python
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

with open("credentials.json", "r") as f:
    creds_info = json.load(f)

credentials = Credentials.from_service_account_info(
    creds_info,
    scopes=['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive']
)

slides_service = build('slides', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
```

## Common Operations

### Create New Presentation

```python
presentation = slides_service.presentations().create(
    body={
        "title": "Presentation Title"
    }
).execute()

presentation_id = presentation["presentationId"]
print(f"Created: https://docs.google.com/presentation/d/{presentation_id}/edit")
```

### Add Slides

```python
# Add a blank slide
slide = slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "createSlide": {
                    "objectId": "slide_001",
                }
            }
        ]
    }
).execute()

# Add slide with specific layout
slide = slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "createSlide": {
                    "objectId": "slide_002",
                    "layoutId": "TITLE_AND_BODY"
                }
            }
        ]
    }
).execute()
```

### Available Layouts

| Layout ID | Description |
|-----------|-------------|
| `BLANK` | Empty slide |
| `TITLE_ONLY` | Title only |
| `TITLE_AND_BODY` | Title and body text |
| `TITLE_AND_TWO_COLUMNS` | Title with two content columns |
| `TITLE_AND_THREE_COLUMNS` | Title with three content columns |
| `SECTION_HEADER` | Section divider |
| `BIG_NUMBER` | Large number display |

### Delete Slide

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {"deleteObject": {"objectId": "slide_id"}}
        ]
    }
).execute()
```

### Duplicate Slide

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "duplicateObject": {
                    "objectId": "source_slide_id",
                    "objectIds": {"duplicate": "new_slide_id"}
                }
            }
        ]
    }
).execute()
```

## Text Operations

### Insert Text

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "insertText": {
                    "objectId": "shape_id",
                    "text": "Hello World"
                }
            }
        ]
    }
).execute()
```

### Replace Text (All Occurrences)

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "replaceAllText": {
                    "containsText": {"text": "{{placeholder}}"},
                    "replaceText": "New Value"
                }
            }
        ]
    }
).execute()
```

### Format Text

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "updateTextStyle": {
                    "objectId": "shape_id",
                    "textRange": {"type": "ALL"},
                    "style": {
                        "bold": True,
                        "italic": False,
                        "fontSize": {
                            "magnitude": 24,
                            "unit": "PT"
                        },
                        "foregroundColor": {
                            "opaqueColor": {"rgbColor": {"red": 1.0, "green": 0.0, "blue": 0.0}}
                        }
                    },
                    "fields": "bold,italic,fontSize,foregroundColor"
                }
            }
        ]
    }
).execute()
```

## Shape Operations

### Create Shape

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "createShape": {
                    "objectId": "shape_001",
                    "shapeType": "RECTANGLE",
                    "elementProperties": {
                        "pageObjectId": "slide_id",
                        "size": {
                            "width": {"magnitude": 200, "unit": "PT"},
                            "height": {"magnitude": 100, "unit": "PT"}
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 100,
                            "translateY": 100,
                            "unit": "PT"
                        }
                    }
                }
            }
        ]
    }
).execute()
```

### Shape Types

| Type | Value |
|------|-------|
| Rectangle | `RECTANGLE` |
| Rounded Rectangle | `ROUNDED_RECTANGLE` |
| Ellipse | `ELLIPSE` |
| Circle | `ELLIPSE` (with equal dimensions) |
| Triangle | `TRIANGLE` |
| Arrow | `RIGHT_ARROW`, `LEFT_ARROW`, `UP_ARROW`, `DOWN_ARROW` |
| Star | `STAR_5_POINT`, `STAR_10_POINT` |

### Update Shape Properties

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "updateShapeProperties": {
                    "objectId": "shape_id",
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                            "solidFill": {
                                "color": {"rgbColor": {"red": 0.2, "green": 0.4, "blue": 0.8}}
                            }
                        },
                        "outline": {
                            "propertyState": "NOT_RENDERED"
                        }
                    },
                    "fields": "shapeBackgroundFill,outline"
                }
            }
        ]
    }
).execute()
```

## Image Operations

### Add Image from URL

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "createImage": {
                    "objectId": "image_001",
                    "url": "https://example.com/image.png",
                    "elementProperties": {
                        "pageObjectId": "slide_id",
                        "size": {
                            "width": {"magnitude": 300, "unit": "PT"},
                            "height": {"magnitude": 200, "unit": "PT"}
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 50,
                            "translateY": 50,
                            "unit": "PT"
                        }
                    }
                }
            }
        ]
    }
).execute()
```

### Add Image from File

```python
# First, upload image to Drive
file_metadata = {"name": "image.png", "mimeType": "image/png"}
media = MediaFileUpload("image.png", mimetype="image/png")

uploaded = drive_service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id"
).execute()

image_id = uploaded.get("id")

# Then add to slide
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "createImage": {
                    "objectId": "image_001",
                    "sourceUrl": f"https://drive.google.com/uc?id={image_id}",
                    "elementProperties": {
                        "pageObjectId": "slide_id",
                        "size": {
                            "width": {"magnitude": 300, "unit": "PT"},
                            "height": {"magnitude": 200, "unit": "PT"}
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 50,
                            "translateY": 50,
                            "unit": "PT"
                        }
                    }
                }
            }
        ]
    }
).execute()
```

## Table Operations

### Create Table

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "createTable": {
                    "objectId": "table_001",
                    "rows": 3,
                    "columns": 4,
                    "elementProperties": {
                        "pageObjectId": "slide_id",
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 50,
                            "translateY": 100,
                            "unit": "PT"
                        }
                    }
                }
            }
        ]
    }
).execute()
```

### Insert Table Text

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "insertText": {
                    "objectId": "table_001",
                    "cellLocation": {"rowIndex": 0, "columnIndex": 0},
                    "text": "Header 1"
                }
            },
            {
                "insertText": {
                    "objectId": "table_001",
                    "cellLocation": {"rowIndex": 0, "columnIndex": 1},
                    "text": "Header 2"
                }
            }
        ]
    }
).execute()
```

## Design Principles

When creating Google Slides presentations, follow these design guidelines:

### Color Selection

Choose a cohesive color palette:
- **Primary color**: Main theme color (headings, key elements)
- **Secondary color**: Supporting elements
- **Accent color**: Call-to-action or highlights
- **Background**: White or light neutral for readability

Common palette examples:
- **Corporate Blue**: Navy (#1C2833), slate (#2E4053), gray (#AAB7B8)
- **Teal Modern**: Teal (#5EA8A7), dark teal (#277884), coral (#FE4447)
- **Minimal Gray**: Dark gray (#2C2C2C), medium gray (#6B6B6B), light gray (#F0F0F0)

### Typography

- Use web-safe fonts: Arial, Helvetica, Times New Roman, Georgia
- Create hierarchy: Title (36-44pt), Headings (24-32pt), Body (14-18pt)
- Maintain consistent line spacing: 1.2-1.5
- Strong contrast between text and background

### Layout Best Practices

- **Two-column layout**: Preferred for slides with charts/tables (40%/60% split)
- **Full-slide layout**: For charts, tables, or images that need maximum space
- **Avoid vertical stacking**: Don't place charts below text in single column
- **Leave whitespace**: Don't overcrowd slides
- **Align elements**: Use grid alignment for consistency

## Slide Reordering

```python
slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {
                "updateSlidesPosition": {
                    "slideObjectIds": ["slide_001", "slide_003", "slide_002"],
                    "insertionIndex": 0
                }
            }
        ]
    }
).execute()
```

## Get Presentation Info

```python
presentation = slides_service.presentations().get(
    presentationId=presentation_id
).execute()

for slide in presentation.get("slides", []):
    slide_id = slide["objectId"]
    print(f"Slide: {slide_id}")
    for element in slide.get("pageElements", []):
        elem_type = list(element.keys())[0]
        elem_id = element.get("objectId")
        print(f"  Element: {elem_type} ({elem_id})")
```

## Get Presentation ID from URL

```python
import re

def get_presentation_id(url):
    """Extract presentation ID from Google Slides URL"""
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not match:
        raise ValueError("Invalid Google Slides URL")
    return match.group(1)

url = "https://docs.google.com/presentation/d/{id}/edit"
presentation_id = get_presentation_id(url)
```

## Export Presentation

```python
import requests

slides_url = f"https://docs.google.com/presentation/d/{presentation_id}/export"
params = {
    "format": "pdf",  # or "pptx"
    "id": presentation_id
}

response = requests.get(slides_url, params=params)
with open("presentation.pdf", "wb") as f:
    f.write(response.content)
```

## Code Style Guidelines

When generating Google Slides code:
- Keep functions focused on single operations
- Use meaningful variable names for object IDs
- Handle batch updates efficiently (multiple requests in one call)
- Validate responses before proceeding
- Log presentation URLs for user reference

