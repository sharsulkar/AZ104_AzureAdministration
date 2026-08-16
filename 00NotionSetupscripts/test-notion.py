import os
import requests

TOKEN = os.environ["NOTION_TOKEN"]
PAGE_ID = os.environ["NOTION_PARENT_PAGE_ID"]

url = f"https://api.notion.com/v1/pages/{PAGE_ID}"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2026-03-11"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print(response.json())