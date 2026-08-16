#!/usr/bin/env python3

import os
import sys
import requests


# ============================================================
# AZ-104 NOTION KNOWLEDGE SYSTEM
# ============================================================
#
# Creates the initial AZ-104 knowledge system in Notion.
#
# Requirements:
#   NOTION_TOKEN
#   NOTION_PARENT_PAGE_ID
#
# Usage:
#   python3 00NotionSetupscripts/setup_notion.py
#
# IMPORTANT:
#   This script is intentionally NOT idempotent.
#   Run it ONCE against an empty AZ-104 parent page.
#
# ============================================================


NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID")

NOTION_VERSION = "2026-03-11"
BASE_URL = "https://api.notion.com/v1"


# ============================================================
# ENVIRONMENT
# ============================================================

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


# ============================================================
# API HELPER
# ============================================================

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
        print("==========================================")
        print(" NOTION API ERROR")
        print("==========================================")
        print()
        print("Method:", method)
        print("Endpoint:", endpoint)
        print("Status:", response.status_code)
        print("Response:")
        print(response.text)
        print()

        sys.exit(1)

    return response.json()


# ============================================================
# VERIFY PARENT
# ============================================================

def verify_parent_page():

    return notion_request(
        "GET",
        f"/pages/{PARENT_PAGE_ID}"
    )


# ============================================================
# CREATE PAGE
# ============================================================

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

    return notion_request(
        "POST",
        "/pages",
        payload
    )


# ============================================================
# CREATE DATABASE
# ============================================================

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

    return notion_request(
        "POST",
        "/databases",
        payload
    )


# ============================================================
# GET DATABASE
#
# Used to reliably retrieve the data_source_id created with
# the database.
# ============================================================

def get_database(database_id):

    return notion_request(
        "GET",
        f"/databases/{database_id}"
    )


# ============================================================
# UPDATE DATA SOURCE
#
# Used to add relation properties after all databases exist.
# ============================================================

def update_data_source(data_source_id, properties):

    payload = {
        "properties": properties
    }

    return notion_request(
        "PATCH",
        f"/data_sources/{data_source_id}",
        payload
    )


# ============================================================
# AZ-104 DOMAINS
# ============================================================

DOMAIN_OPTIONS = [
    {
        "name": "Identity & Governance",
        "color": "blue"
    },
    {
        "name": "Storage",
        "color": "green"
    },
    {
        "name": "Compute",
        "color": "orange"
    },
    {
        "name": "Networking",
        "color": "purple"
    },
    {
        "name": "Monitoring",
        "color": "yellow"
    },
    {
        "name": "Backup & DR",
        "color": "red"
    },
    {
        "name": "Integrated",
        "color": "pink"
    },
]


# ============================================================
# DATABASE SCHEMAS
# ============================================================

DATABASES = {

    # --------------------------------------------------------
    # KNOWLEDGE
    # --------------------------------------------------------

    "Knowledge": {

        "Concept": {
            "title": {}
        },

        "Domain": {
            "select": {
                "options": DOMAIN_OPTIONS
            }
        },

        "Service": {
            "rich_text": {}
        },

        "Confidence": {
            "select": {
                "options": [
                    {
                        "name": "Low",
                        "color": "red"
                    },
                    {
                        "name": "Medium",
                        "color": "yellow"
                    },
                    {
                        "name": "High",
                        "color": "green"
                    },
                ]
            }
        },

        "Status": {
            "select": {
                "options": [
                    {
                        "name": "Not Started",
                        "color": "gray"
                    },
                    {
                        "name": "Learning",
                        "color": "yellow"
                    },
                    {
                        "name": "Practiced",
                        "color": "blue"
                    },
                    {
                        "name": "Mastered",
                        "color": "green"
                    },
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


    # --------------------------------------------------------
    # LABS
    # --------------------------------------------------------

    "Labs": {

        "Lab": {
            "title": {}
        },

        "Domain": {
            "select": {
                "options": DOMAIN_OPTIONS
            }
        },

        "Services": {
            "rich_text": {}
        },

        "Difficulty": {
            "select": {
                "options": [
                    {
                        "name": "Beginner",
                        "color": "green"
                    },
                    {
                        "name": "Intermediate",
                        "color": "yellow"
                    },
                    {
                        "name": "Advanced",
                        "color": "red"
                    },
                ]
            }
        },

        "Status": {
            "select": {
                "options": [
                    {
                        "name": "Not Started",
                        "color": "gray"
                    },
                    {
                        "name": "In Progress",
                        "color": "yellow"
                    },
                    {
                        "name": "Completed",
                        "color": "green"
                    },
                    {
                        "name": "Revisit",
                        "color": "red"
                    },
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


    # --------------------------------------------------------
    # SCENARIOS
    # --------------------------------------------------------

    "Scenarios": {

        "Scenario": {
            "title": {}
        },

        "Domain": {
            "select": {
                "options": DOMAIN_OPTIONS
            }
        },

        "Difficulty": {
            "select": {
                "options": [
                    {
                        "name": "Beginner",
                        "color": "green"
                    },
                    {
                        "name": "Intermediate",
                        "color": "yellow"
                    },
                    {
                        "name": "Advanced",
                        "color": "red"
                    },
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
                    {
                        "name": "Not Started",
                        "color": "gray"
                    },
                    {
                        "name": "Working",
                        "color": "yellow"
                    },
                    {
                        "name": "Solved",
                        "color": "green"
                    },
                ]
            }
        },
    },


    # --------------------------------------------------------
    # TROUBLESHOOTING
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # MISTAKE LOG
    # --------------------------------------------------------

    "Mistake Log": {

        "Question": {
            "title": {}
        },

        "Domain": {
            "select": {
                "options": DOMAIN_OPTIONS
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
                    {
                        "name": "Knowledge Gap",
                        "color": "red"
                    },
                    {
                        "name": "Misread Question",
                        "color": "orange"
                    },
                    {
                        "name": "Confused Services",
                        "color": "yellow"
                    },
                    {
                        "name": "Forgot Detail",
                        "color": "blue"
                    },
                    {
                        "name": "Reasoning Error",
                        "color": "purple"
                    },
                ]
            }
        },

        "Confidence": {
            "select": {
                "options": [
                    {
                        "name": "Low",
                        "color": "red"
                    },
                    {
                        "name": "Medium",
                        "color": "yellow"
                    },
                    {
                        "name": "High",
                        "color": "green"
                    },
                ]
            }
        },

        "Review Date": {
            "date": {}
        },
    },


    # --------------------------------------------------------
    # MOCK TESTS
    # --------------------------------------------------------

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
                    {
                        "name": "Planned",
                        "color": "gray"
                    },
                    {
                        "name": "Completed",
                        "color": "green"
                    },
                    {
                        "name": "Review Required",
                        "color": "red"
                    },
                ]
            }
        },
    },


    # --------------------------------------------------------
    # REVIEW QUEUE
    # --------------------------------------------------------

    "Review Queue": {

        "Topic": {
            "title": {}
        },

        "Type": {
            "select": {
                "options": [
                    {
                        "name": "Concept",
                        "color": "blue"
                    },
                    {
                        "name": "Lab",
                        "color": "green"
                    },
                    {
                        "name": "Mistake",
                        "color": "red"
                    },
                    {
                        "name": "Troubleshooting",
                        "color": "orange"
                    },
                    {
                        "name": "Mock Question",
                        "color": "purple"
                    },
                ]
            }
        },

        "Priority": {
            "select": {
                "options": [
                    {
                        "name": "Low",
                        "color": "green"
                    },
                    {
                        "name": "Medium",
                        "color": "yellow"
                    },
                    {
                        "name": "High",
                        "color": "red"
                    },
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
                    {
                        "name": "Queued",
                        "color": "gray"
                    },
                    {
                        "name": "Reviewing",
                        "color": "yellow"
                    },
                    {
                        "name": "Complete",
                        "color": "green"
                    },
                ]
            }
        },
    },


    # --------------------------------------------------------
    # SERVICES
    # --------------------------------------------------------

    "Services": {

        "Service": {
            "title": {}
        },

        "Category": {
            "select": {
                "options": [
                    {
                        "name": "Identity",
                        "color": "blue"
                    },
                    {
                        "name": "Governance",
                        "color": "purple"
                    },
                    {
                        "name": "Compute",
                        "color": "orange"
                    },
                    {
                        "name": "Storage",
                        "color": "green"
                    },
                    {
                        "name": "Networking",
                        "color": "pink"
                    },
                    {
                        "name": "Monitoring",
                        "color": "yellow"
                    },
                    {
                        "name": "Backup",
                        "color": "red"
                    },
                    {
                        "name": "Security",
                        "color": "gray"
                    },
                ]
            }
        },

        "Exam Relevance": {
            "select": {
                "options": [
                    {
                        "name": "High",
                        "color": "red"
                    },
                    {
                        "name": "Medium",
                        "color": "yellow"
                    },
                    {
                        "name": "Low",
                        "color": "green"
                    },
                ]
            }
        },
    },
        # --------------------------------------------------------
    # SERVICE COMPARISONS
    # --------------------------------------------------------

    "Service Comparisons": {

        "Comparison": {
            "title": {}
        },

        "Category": {
            "select": {
                "options": [
                    {
                        "name": "Identity",
                        "color": "blue"
                    },
                    {
                        "name": "Governance",
                        "color": "purple"
                    },
                    {
                        "name": "Storage",
                        "color": "green"
                    },
                    {
                        "name": "Compute",
                        "color": "orange"
                    },
                    {
                        "name": "Networking",
                        "color": "pink"
                    },
                    {
                        "name": "Monitoring",
                        "color": "yellow"
                    },
                    {
                        "name": "Security",
                        "color": "red"
                    },
                ]
            }
        },

        "Services": {
            "rich_text": {}
        },

        "Decision Question": {
            "rich_text": {}
        },

        "Key Difference": {
            "rich_text": {}
        },

        "Exam Trap": {
            "rich_text": {}
        },
    },

    # --------------------------------------------------------
    # MS LEARN
    # --------------------------------------------------------

    "MS Learn": {

        "Resource": {
            "title": {}
        },

        "URL": {
            "url": {}
        },

        "Topic": {
            "rich_text": {}
        },

        "Notes": {
            "rich_text": {}
        },

        "Last Verified": {
            "date": {}
        },
    },
}


# ============================================================
# RELATION DEFINITIONS
# ============================================================
#
# Format:
#
#   source database:
#       property name: target database
#
# These are intentionally one-way relations.
# We are keeping the schema simple rather than creating a
# giant web of bidirectional relations.
#
# ============================================================

RELATIONS = {

    "Knowledge": {
        "Labs": "Labs",
        "Scenarios": "Scenarios",
        "Troubleshooting": "Troubleshooting",
        "Mistakes": "Mistake Log",
        "Mock Tests": "Mock Tests",
        "Services": "Services",
        "MS Learn": "MS Learn",
    },

    "Labs": {
        "Concepts": "Knowledge",
        "Scenarios": "Scenarios",
        "Services": "Services",
    },

    "Scenarios": {
        "Concepts": "Knowledge",
        "Labs": "Labs",
        "Services": "Services",
        "Troubleshooting": "Troubleshooting",
    },

    "Troubleshooting": {
        "Concepts": "Knowledge",
        "Labs": "Labs",
        "Services": "Services",
    },

    "Mistake Log": {
        "Concepts": "Knowledge",
        "Labs": "Labs",
        "Scenarios": "Scenarios",
        "Mock Tests": "Mock Tests",
    },

    "Mock Tests": {
        "Concepts": "Knowledge",
        "Mistakes": "Mistake Log",
    },

    "Review Queue": {
        "Concepts": "Knowledge",
        "Labs": "Labs",
        "Mistakes": "Mistake Log",
        "Troubleshooting": "Troubleshooting",
    },

    "Service Comparisons": {
        "Knowledge": "Knowledge",
        "Services": "Services",
        "Labs": "Labs",
    },

    "MS Learn": {
        "Concepts": "Knowledge",
    },
}


# ============================================================
# NAVIGATION PAGES
# ============================================================

NAVIGATION_PAGES = [

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


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("==========================================")
    print(" AZ-104 NOTION KNOWLEDGE SYSTEM")
    print("==========================================")
    print()

    # --------------------------------------------------------
    # Verify parent
    # --------------------------------------------------------

    print("Verifying parent page...")

    verify_parent_page()

    print("Parent page verified.")
    print()


    # --------------------------------------------------------
    # Create navigation pages
    # --------------------------------------------------------

    print("Creating navigation pages...")
    print()

    created_pages = 0

    for title in NAVIGATION_PAGES:

        print(f"  Creating page: {title}")

        create_page(
            PARENT_PAGE_ID,
            title
        )

        created_pages += 1

    print()
    print(
        f"Created {created_pages} navigation pages."
    )


    # --------------------------------------------------------
    # Create databases
    # --------------------------------------------------------

    print()
    print("Creating databases...")
    print()

    database_ids = {}
    data_source_ids = {}

    for name, properties in DATABASES.items():

        print(
            f"  Creating database: {name}"
        )

        response = create_database(
            PARENT_PAGE_ID,
            name,
            properties
        )

        database_id = response.get("id")

        if not database_id:

            print(
                f"ERROR: No database ID returned "
                f"for {name}."
            )

            sys.exit(1)

        database_ids[name] = database_id

        print(
            f"    Database ID: {database_id}"
        )

        # ----------------------------------------------------
        # Retrieve database to get data source ID
        # ----------------------------------------------------

        database = get_database(
            database_id
        )

        sources = database.get(
            "data_sources",
            []
        )

        if not sources:

            print(
                f"ERROR: No data source found "
                f"for database {name}."
            )

            sys.exit(1)

        data_source_id = sources[0].get("id")

        if not data_source_id:

            print(
                f"ERROR: Data source has no ID "
                f"for database {name}."
            )

            sys.exit(1)

        data_source_ids[name] = data_source_id

        print(
            f"    Data Source ID: {data_source_id}"
        )


    # --------------------------------------------------------
    # Create relationships
    # --------------------------------------------------------

    print()
    print("Creating database relationships...")
    print()

    relation_count = 0

    for source_name, relations in RELATIONS.items():

        source_data_source_id = data_source_ids.get(
            source_name
        )

        if not source_data_source_id:

            print(
                f"WARNING: Missing data source for "
                f"{source_name}"
            )

            continue

        relation_properties = {}

        for property_name, target_name in relations.items():

            target_data_source_id = data_source_ids.get(
                target_name
            )

            if not target_data_source_id:

                print(
                    f"WARNING: Missing target data source "
                    f"{target_name}"
                )

                continue

            relation_properties[property_name] = {
                "relation": {
                "single_property": {},
                "data_source_id": target_data_source_id
            }
        }

        if not relation_properties:
            continue

        print(
            f"  Updating: {source_name}"
        )

        update_data_source(
            source_data_source_id,
            relation_properties
        )

        for property_name, target_name in relations.items():

            print(
                f"    {property_name} -> {target_name}"
            )

            relation_count += 1


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("==========================================")
    print(" AZ-104 NOTION SYSTEM CREATED")
    print("==========================================")
    print()

    print(
        f"Navigation pages : {created_pages}"
    )

    print(
        f"Databases        : {len(DATABASES)}"
    )

    print(
        f"Relationships     : {relation_count}"
    )

    print()

    print("Databases created:")

    for name in DATABASES:

        print(
            f"  - {name}"
        )

    print()

    print("Relationship setup complete.")

    print()
    print("Next:")
    print("1. Open Notion.")
    print("2. Verify the databases.")
    print("3. Verify a few relation columns.")
    print("4. Do NOT run this script again.")
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()