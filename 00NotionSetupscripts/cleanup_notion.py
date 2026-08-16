#!/usr/bin/env python3

import os
import sys
import requests


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


def get_children(block_id):

    response = requests.get(
        f"{BASE_URL}/blocks/{block_id}/children",
        headers=HEADERS,
        params={"page_size": 100},
    )

    if not response.ok:
        print("ERROR reading children")
        print(response.status_code)
        print(response.text)
        sys.exit(1)

    return response.json().get("results", [])


def delete_block(block_id):

    response = requests.delete(
        f"{BASE_URL}/blocks/{block_id}",
        headers=HEADERS,
    )

    if not response.ok:
        print(f"ERROR deleting {block_id}")
        print(response.status_code)
        print(response.text)
        return False

    return True


print()
print("==========================================")
print(" NOTION AZ-104 CLEANUP")
print("==========================================")
print()

print(f"Parent page: {PARENT_ID}")
print()

children = get_children(PARENT_ID)

print(f"Found {len(children)} direct children.")
print()

if not children:
    print("Nothing to delete.")
    sys.exit(0)


print("The following objects will be moved to Notion Trash:")
print()

for child in children:

    block_type = child.get("type")
    block_id = child.get("id")

    if block_type == "child_page":

        title = child.get(
            "child_page",
            {}
        ).get(
            "title",
            "(untitled page)"
        )

        print(f"PAGE      : {title}")
        print(f"            {block_id}")

    elif block_type == "child_database":

        title = child.get(
            "child_database",
            {}
        ).get(
            "title",
            "(untitled database)"
        )

        print(f"DATABASE  : {title}")
        print(f"            {block_id}")

    else:

        print(f"{block_type.upper():10}: {block_id}")

print()
print("Starting cleanup...")
print()


deleted = 0
failed = 0

for child in children:

    block_id = child.get("id")

    if delete_block(block_id):

        deleted += 1

        print(
            f"TRASHED  {child.get('type')} "
            f"{block_id}"
        )

    else:

        failed += 1


print()
print("==========================================")
print(" CLEANUP COMPLETE")
print("==========================================")
print()

print(f"Deleted: {deleted}")
print(f"Failed:  {failed}")

print()

if failed:
    print("Some objects could not be deleted.")
    sys.exit(1)

print("Parent page is ready for a fresh setup.")