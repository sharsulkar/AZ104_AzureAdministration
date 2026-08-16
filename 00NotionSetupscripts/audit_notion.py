#!/usr/bin/env python3

import os
import sys
import requests
from collections import defaultdict


TOKEN = os.environ.get("NOTION_TOKEN")
PARENT_ID = os.environ.get("NOTION_PARENT_PAGE_ID")

if not TOKEN:
    print("ERROR: NOTION_TOKEN is not set.")
    sys.exit(1)

if not PARENT_ID:
    print("ERROR: NOTION_PARENT_PAGE_ID is not set.")
    sys.exit(1)


HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2026-03-11",
    "Content-Type": "application/json",
}

BASE_URL = "https://api.notion.com/v1"


def request(method, endpoint, payload=None):

    response = requests.request(
        method,
        BASE_URL + endpoint,
        headers=HEADERS,
        json=payload,
    )

    if not response.ok:

        print()
        print("NOTION API ERROR")
        print("Status:", response.status_code)
        print("Response:", response.text)
        print()

        sys.exit(1)

    return response.json()


def get_page_title(page):

    for prop in page.get("properties", {}).values():

        if prop.get("type") == "title":

            return "".join(
                item.get("plain_text", "")
                for item in prop.get("title", [])
            )

    return ""


def search(object_type):

    payload = {
        "filter": {
            "property": "object",
            "value": object_type
        },
        "page_size": 100
    }

    return request(
        "POST",
        "/search",
        payload
    ).get("results", [])


def get_database(database_id):

    return request(
        "GET",
        f"/databases/{database_id}"
    )


print()
print("==========================================")
print(" NOTION AZ-104 AUDIT")
print("==========================================")
print()

print("Parent page:")
print(PARENT_ID)
print()


# ============================================================
# PAGES
# ============================================================

print("PAGES")
print("------------------------------------------")

pages = search("page")

page_groups = defaultdict(list)

for page in pages:

    parent = page.get("parent", {})

    if parent.get("page_id") != PARENT_ID:
        continue

    title = get_page_title(page)

    if title:
        page_groups[title].append(page)


for title in sorted(page_groups):

    items = page_groups[title]

    print()
    print(f"{title} ({len(items)})")

    for item in items:

        print(
            f"  PAGE ID: {item['id']}"
        )


# ============================================================
# DATA SOURCES
# ============================================================

print()
print()
print("DATABASES / DATA SOURCES")
print("------------------------------------------")

sources = search("data_source")

database_groups = defaultdict(list)

for source in sources:

    parent = source.get("parent", {})

    database_id = parent.get("database_id")

    if not database_id:
        continue

    database = get_database(database_id)

    database_parent = database.get(
        "parent",
        {}
    )

    if database_parent.get(
        "page_id"
    ) != PARENT_ID:

        continue

    title = "".join(
        item.get(
            "plain_text",
            ""
        )
        for item in database.get(
            "title",
            []
        )
    )

    if not title:
        title = "(untitled)"

    database_groups[title].append({
        "database_id": database_id,
        "data_source_id": source["id"],
    })


for title in sorted(database_groups):

    items = database_groups[title]

    print()
    print(
        f"{title} ({len(items)})"
    )

    for item in items:

        print(
            f"  DATABASE ID: "
            f"{item['database_id']}"
        )

        print(
            f"  DATA SOURCE ID: "
            f"{item['data_source_id']}"
        )


# ============================================================
# SUMMARY
# ============================================================

duplicate_pages = [
    title
    for title, items in page_groups.items()
    if len(items) > 1
]

duplicate_databases = [
    title
    for title, items in database_groups.items()
    if len(items) > 1
]


print()
print("==========================================")
print(" SUMMARY")
print("==========================================")
print()

print(
    "Pages found:",
    sum(
        len(items)
        for items in page_groups.values()
    )
)

print(
    "Duplicate page types:",
    len(duplicate_pages)
)

print()

print(
    "Databases found:",
    sum(
        len(items)
        for items in database_groups.values()
    )
)

print(
    "Duplicate database types:",
    len(duplicate_databases)
)

print()

if duplicate_pages:

    print("Duplicate pages:")

    for title in duplicate_pages:
        print(
            f"  - {title}"
        )

    print()

if duplicate_databases:

    print("Duplicate databases:")

    for title in duplicate_databases:
        print(
            f"  - {title}"
        )

    print()

print("Audit complete.")