#!/usr/bin/env python3

import os
import sys
import requests


# ============================================================
# AZ-104 Notion Knowledge System Bootstrap
# ============================================================
#
# Requirements:
#   NOTION_TOKEN
#   NOTION_PARENT_PAGE_ID
#
# Usage:
#   python3 scripts/setup_notion.py
#
# ============================================================


NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID")

NOTION_VERSION = "2026-03-11"
BASE_URL = "https://api.notion.com/v1"


# ------------------------------------------------------------
# Validate environment
# ------------------------------------------------------------

if not NOTION_TOKEN:
    print("ERROR: NOTION_TOKEN is not set.")
    sys.exit(1)

if not PARENT_PAGE_ID:
    print("ERROR: NOTION_PARENT_PAGE_ID is not set.")
    sys.exit(1)


HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


# ------------------------------------------------------------
# API helper
# ------------------------------------------------------------

def notion_request(method, endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"

    response = requests.request(
        method,
        url,
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


# ------------------------------------------------------------
# Create child page
# ------------------------------------------------------------

def create_page(parent_id, title):
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": parent_id,
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        },
                    }
                ]
            }
        },
    }

    return notion_request("POST", "/pages", payload)


# ------------------------------------------------------------
# Create database
# ------------------------------------------------------------

def create_database(parent_id, title, properties):
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": parent_id,
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": title
                },
            }
        ],
        "is_inline": False,
        "initial_data_source": {
            "properties": properties
        },
    }

    return notion_request("POST", "/databases", payload)


# ------------------------------------------------------------
# Database schemas
# ------------------------------------------------------------

DATABASES = {

    "Knowledge": {
        "Concept": {
            "title": {}
        },
        "Domain": {
            "select": {
                "options": [
                    {"name": "Identity & Governance", "color": "blue"},
                    {"name": "Storage", "color": "green"},
                    {"name": "Compute", "color": "orange"},
                    {"name": "Networking", "color": "purple"},
                    {"name": "Monitoring", "color": "yellow"},
                    {"name": "Backup & DR", "color": "red"},
                ]
            }
        },
        "Service": {
            "rich_text": {}
        },
        "Confidence": {
            "select": {
                "options": [
                    {"name": "Low", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "High", "color": "green"},
                ]
            }
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "Not Started", "color": "gray"},
                    {"name": "Learning", "color": "yellow"},
                    {"name": "Practiced", "color": "blue"},
                    {"name": "Mastered", "color": "green"},
                ]
            }
        },
        "Last Reviewed": {
            "date": {}
        },
        "Next Review": {
            "date": {}
        },
    },


    "Labs": {
        "Lab": {
            "title": {}
        },
        "Domain": {
            "select": {
                "options": [
                    {"name": "Identity & Governance", "color": "blue"},
                    {"name": "Storage", "color": "green"},
                    {"name": "Compute", "color": "orange"},
                    {"name": "Networking", "color": "purple"},
                    {"name": "Monitoring", "color": "yellow"},
                    {"name": "Backup & DR", "color": "red"},
                    {"name": "Integrated", "color": "pink"},
                ]
            }
        },
        "Services": {
            "rich_text": {}
        },
        "Difficulty": {
            "select": {
                "options": [
                    {"name": "Beginner", "color": "green"},
                    {"name": "Intermediate", "color": "yellow"},
                    {"name": "Advanced", "color": "red"},
                ]
            }
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "Not Started", "color": "gray"},
                    {"name": "In Progress", "color": "yellow"},
                    {"name": "Completed", "color": "green"},
                    {"name": "Revisit", "color": "red"},
                ]
            }
        },
        "GitHub Path": {
            "rich_text": {}
        },
        "Key Concepts": {
            "rich_text": {}
        },
    },


    "Scenarios": {
        "Scenario": {
            "title": {}
        },
        "Domain": {
            "select": {
                "options": [
                    {"name": "Identity & Governance", "color": "blue"},
                    {"name": "Storage", "color": "green"},
                    {"name": "Compute", "color": "orange"},
                    {"name": "Networking", "color": "purple"},
                    {"name": "Monitoring", "color": "yellow"},
                    {"name": "Integrated", "color": "pink"},
                ]
            }
        },
        "Difficulty": {
            "select": {
                "options": [
                    {"name": "Beginner", "color": "green"},
                    {"name": "Intermediate", "color": "yellow"},
                    {"name": "Advanced", "color": "red"},
                ]
            }
        },
        "Services": {
            "rich_text": {}
        },
        "Requirements": {
            "rich_text": {}
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "Not Started", "color": "gray"},
                    {"name": "Working", "color": "yellow"},
                    {"name": "Solved", "color": "green"},
                ]
            }
        },
    },


    "Troubleshooting": {
        "Incident": {
            "title": {}
        },
        "Symptoms": {
            "rich_text": {}
        },
        "Services": {
            "rich_text": {}
        },
        "Possible Causes": {
            "rich_text": {}
        },
        "Diagnostic Steps": {
            "rich_text": {}
        },
        "Root Cause": {
            "rich_text": {}
        },
        "Resolution": {
            "rich_text": {}
        },
    },


    "Mistake Log": {
        "Question": {
            "title": {}
        },
        "Domain": {
            "select": {
                "options": [
                    {"name": "Identity & Governance", "color": "blue"},
                    {"name": "Storage", "color": "green"},
                    {"name": "Compute", "color": "orange"},
                    {"name": "Networking", "color": "purple"},
                    {"name": "Monitoring", "color": "yellow"},
                ]
            }
        },
        "Topic": {
            "rich_text": {}
        },
        "My Answer": {
            "rich_text": {}
        },
        "Correct Answer": {
            "rich_text": {}
        },
        "Why Wrong": {
            "rich_text": {}
        },
        "Root Cause": {
            "select": {
                "options": [
                    {"name": "Knowledge Gap", "color": "red"},
                    {"name": "Misread Question", "color": "orange"},
                    {"name": "Confused Services", "color": "yellow"},
                    {"name": "Forgot Detail", "color": "blue"},
                    {"name": "Reasoning Error", "color": "purple"},
                ]
            }
        },
        "Confidence": {
            "select": {
                "options": [
                    {"name": "Low", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "High", "color": "green"},
                ]
            }
        },
        "Review Date": {
            "date": {}
        },
    },


    "Mock Tests": {
        "Mock": {
            "title": {}
        },
        "Date": {
            "date": {}
        },
        "Score": {
            "number": {}
        },
        "Domain": {
            "rich_text": {}
        },
        "Weak Areas": {
            "rich_text": {}
        },
        "Questions Missed": {
            "number": {}
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "Planned", "color": "gray"},
                    {"name": "Completed", "color": "green"},
                    {"name": "Review Required", "color": "red"},
                ]
            }
        },
    },


    "Review Queue": {
        "Topic": {
            "title": {}
        },
        "Type": {
            "select": {
                "options": [
                    {"name": "Concept", "color": "blue"},
                    {"name": "Lab", "color": "green"},
                    {"name": "Mistake", "color": "red"},
                    {"name": "Troubleshooting", "color": "orange"},
                    {"name": "Mock Question", "color": "purple"},
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "Low", "color": "green"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "High", "color": "red"},
                ]
            }
        },
        "Reason": {
            "rich_text": {}
        },
        "Review Date": {
            "date": {}
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "Queued", "color": "gray"},
                    {"name": "Reviewing", "color": "yellow"},
                    {"name": "Complete", "color": "green"},
                ]
            }
        },
    },
}


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print()
    print("==========================================")
    print(" AZ-104 Notion Knowledge System")
    print("==========================================")
    print()

    # Verify parent page
    print("Verifying parent page...")

    parent = notion_request(
        "GET",
        f"/pages/{PARENT_PAGE_ID}"
    )

    print("Parent page verified.")
    print()

    # --------------------------------------------------------
    # Create navigation pages
    # --------------------------------------------------------

    pages = [
        "00 - Dashboard",
        "01 - Exam Domains",
        "02 - Azure Concepts",
        "03 - Labs",
        "04 - Scenarios",
        "05 - Troubleshooting",
        "06 - Mistake Log",
        "07 - Decision Log",
        "08 - Service Comparisons",
        "09 - Exam Search Skills",
        "10 - Mock Tests",
        "11 - Review Queue",
    ]

    print("Creating knowledge system pages...")
    print()

    for title in pages:

        print(f"Creating page: {title}")

        create_page(
            PARENT_PAGE_ID,
            title
        )

    # --------------------------------------------------------
    # Create databases
    # --------------------------------------------------------

    print()
    print("Creating databases...")
    print()

    for name, properties in DATABASES.items():

        print(f"Creating database: {name}")

        response = create_database(
            PARENT_PAGE_ID,
            name,
            properties
        )

        print(
            f"  Database ID: {response.get('id')}"
        )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print()
    print("==========================================")
    print(" AZ-104 Notion system created successfully")
    print("==========================================")
    print()
    print("Created pages:")
    print(f"  {len(pages)}")

    print()
    print("Created databases:")
    print(f"  {len(DATABASES)}")

    print()
    print("Next step:")
    print("Open your AZ-104 Knowledge System page in Notion")
    print("and verify the structure.")
    print()


if __name__ == "__main__":
    main()