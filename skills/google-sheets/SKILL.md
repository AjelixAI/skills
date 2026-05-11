---
name: google-sheets
description: When Ajelix needs to work with google sheets. Triggers on: (1) Google Sheets URLs, (2) when asked to connect/analyze/import data from Google Sheets, (3) when asked to write/add/update data in Google Sheets
version: "2.1.0"
---

# Google Sheets
allowed-tools: *

## Purpose & Output

### Reading (Public / Read-Only)

## Reading Public Sheets (No Credentials)

### Quick Start
Extract data from public Google Sheets (anyone with link) into pandas. Delegate analysis to `data-analyst`, viz to `dashboard-builder`/`single-chart-builder`.

```python
import re
import pandas as pd

def read_google_sheet(url):
    """Read a public Google Sheet (anyone with link)"""
    # Extract sheet_id from URL (e.g., /d/{id}/edit#gid=0)
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if not match:
        raise ValueError("Invalid Google Sheets URL")
    sheet_id = match.group(1)
    
    # Export to xlsx (public "Anyone with link")
    xlsx_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    return pd.read_excel(xlsx_url)

# Usage: Paste full public link
url = "https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0"
df = read_google_sheet(url)
print(df.head())
```

### Writing / Manipulation (Credentials Required)
Create, update, add data to Google Sheets using service account authentication. Requires service account JSON credentials and sheet sharing permissions.

CRITICAL: Always include "valueInputOption": "USER_ENTERED" when you write data using API. Otherwise, formuals will not work correctly.


## Prerequisites

- Service account JSON file with: `client_email`, `private_key`, `project_id`
- Share the Sheet with the service account email (Editor permission)
- Install packages: `pip install google-auth google-auth-oauthlib requests`

## Authentication

```python
import json
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import requests

with open("credentials.json", "r") as f:
    creds_info = json.load(f)

credentials = Credentials.from_service_account_info(
    creds_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
credentials.refresh(Request())
token = credentials.token
```

## Common Operations

### Get Sheet ID from Metadata

```python
response = requests.get(
    f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}",
    headers={"Authorization": f"Bearer {token}"}
)
for sheet in response.json()["sheets"]:
    name = sheet["properties"]["title"]
    sheet_id = sheet["properties"]["sheetId"]
```

### Write Data

```python
url = f"https://sheets.googleapis.com/v4/spreadsheets/{id}/values:batchUpdate"
body = {
    "valueInputOption": "USER_ENTERED",
    "data": [
        {"range": "Sheet1!A1", "values": [["Value"]]},
        {"range": "Sheet1!B2", "values": [["=SUM(A1:A10)"]]}
    ]
}
requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body)
```

### Create Sheet

```python
url = f"https://sheets.googleapis.com/v4/spreadsheets/{id}:batchUpdate"
body = {
    "requests": [
        {"addSheet": {"properties": {"title": "NewSheet", "sheetId": 1001}}}
    ]
}
requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body)
```

### Delete Sheet

```python
body = {"requests": [{"deleteSheet": {"sheetId": sheet_id}}]}
requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body)
```

### Add Column Chart

```python
body = {
    "requests": [
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Chart Title",
                        "basicChart": {
                            "chartType": "COLUMN",
                            "legendPosition": "BOTTOM_LEGEND",
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "X-Axis"},
                                {"position": "LEFT_AXIS", "title": "Y-Axis"}
                            ],
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [{"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 5, "startColumnIndex": 0, "endColumnIndex": 1}]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 5, "startColumnIndex": 1, "endColumnIndex": 2}]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS"
                                }
                            ],
                            "headerCount": 1
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {"sheetId": sheet_id, "rowIndex": 10, "columnIndex": 0}
                        }
                    }
                }
            }
        }
    ]
}
requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body)
```

### Add Pie Chart

```python
body = {
    "requests": [
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Distribution",
                        "pieChart": {
                            "legendPosition": "BOTTOM_LEGEND",
                            "domain": {
                                "sourceRange": {
                                    "sources": [{"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 3, "startColumnIndex": 0, "endColumnIndex": 1}]
                                }
                            },
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [{"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 3, "startColumnIndex": 1, "endColumnIndex": 2}]
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {"sheetId": sheet_id, "rowIndex": 10, "columnIndex": 0}
                        }
                    }
                }
            }
        }
    ]
}
requests.post(url, headers={"Authorization": f"Bearer {token}"}, json=body)
```

## Chart Types

| Type | Value |
|------|-------|
| Column | `COLUMN` |
| Bar | `BAR` |
| Line | `LINE` |
| Pie | `PIE` |
| Area | `AREA` |
| Scatter | `SCATTER` |

## Common Formulas

| Formula | Description |
|---------|-------------|
| `=SUM(A1:A10)` | Sum range |
| `=AVERAGE(A1:A10)` | Average |
| `=COUNT(A:A)` | Count values |
| `=COUNTBLANK(C:C)` | Count blanks |
| `=IF(A1>10,"Yes","No")` | Conditional |
| `=COUNTIF(A:A,"Yes")` | Count matches |
| `=TODAY()` | Current date |
| `=NOW()` | Current datetime |

