#!/usr/bin/env python3

import os
import sys
import time
import requests


# ============================================================
# AZ-104 NOTION RESET + SEED
# ============================================================
#
# PURPOSE
#
#   Deletes existing records from the AZ-104 knowledge
#   databases and reseeds the initial study universe.
#
# IMPORTANT
#
#   This script deletes/archives DATABASE RECORDS.
#   It does NOT delete the databases themselves.
#
#   It does NOT delete the navigation pages.
#
#
# REQUIREMENTS
#
#   NOTION_TOKEN
#   NOTION_PARENT_PAGE_ID
#
#
# RUN
#
#   python3 00NotionSetupscripts/seed_notion.py
#
# ============================================================


TOKEN = os.environ.get("NOTION_TOKEN")
PARENT_ID = os.environ.get("NOTION_PARENT_PAGE_ID")

NOTION_VERSION = "2026-03-11"
BASE_URL = "https://api.notion.com/v1"


# ============================================================
# VALIDATION
# ============================================================

if not TOKEN:
    print("ERROR: NOTION_TOKEN is not set.")
    sys.exit(1)

if not PARENT_ID:
    print("ERROR: NOTION_PARENT_PAGE_ID is not set.")
    sys.exit(1)


HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


# ============================================================
# API HELPER
# ============================================================

def notion_request(method, endpoint, payload=None):

    response = requests.request(
        method,
        f"{BASE_URL}{endpoint}",
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

    if response.text:
        return response.json()

    return {}


# ============================================================
# GET CHILDREN OF PARENT PAGE
# ============================================================

def get_children(block_id):

    results = []
    cursor = None

    while True:

        params = {
            "page_size": 100
        }

        if cursor:
            params["start_cursor"] = cursor

        response = requests.get(
            f"{BASE_URL}/blocks/{block_id}/children",
            headers=HEADERS,
            params=params,
        )

        if not response.ok:

            print()
            print("ERROR reading page children")
            print("Status:", response.status_code)
            print("Response:", response.text)
            sys.exit(1)

        data = response.json()

        results.extend(
            data.get("results", [])
        )

        if not data.get("has_more"):
            break

        cursor = data.get("next_cursor")

    return results


# ============================================================
# FIND CHILD DATABASES
# ============================================================

def find_databases():

    children = get_children(PARENT_ID)

    databases = {}

    for child in children:

        if child.get("type") != "child_database":
            continue

        database_id = child.get("id")

        title = (
            child
            .get("child_database", {})
            .get("title", "")
        )

        if title:
            databases[title] = database_id

    return databases


# ============================================================
# GET DATABASE
# ============================================================

def get_database(database_id):

    return notion_request(
        "GET",
        f"/databases/{database_id}"
    )


# ============================================================
# GET DATA SOURCE ID
# ============================================================

def get_data_source_id(database_id):

    database = get_database(database_id)

    sources = database.get(
        "data_sources",
        []
    )

    if not sources:

        print()
        print(
            f"ERROR: No data source found for "
            f"database {database_id}"
        )
        print()

        sys.exit(1)

    return sources[0]["id"]


# ============================================================
# QUERY DATA SOURCE
# ============================================================

def query_data_source(data_source_id):

    results = []
    cursor = None

    while True:

        payload = {
            "page_size": 100
        }

        if cursor:
            payload["start_cursor"] = cursor

        response = requests.post(
            f"{BASE_URL}/data_sources/{data_source_id}/query",
            headers=HEADERS,
            json=payload,
        )

        if not response.ok:

            print()
            print("ERROR querying data source")
            print("Status:", response.status_code)
            print("Response:", response.text)
            print()

            sys.exit(1)

        data = response.json()

        results.extend(
            data.get("results", [])
        )

        if not data.get("has_more"):
            break

        cursor = data.get("next_cursor")

    return results


# ============================================================
# DELETE / ARCHIVE DATABASE RECORDS
# ============================================================

def clear_data_source(data_source_id, database_name):

    print(
        f"Clearing records: {database_name}"
    )

    pages = query_data_source(
        data_source_id
    )

    if not pages:
        print("  Already empty.")
        return

    print(
        f"  Found {len(pages)} records."
    )

    trashed = 0

    for page in pages:

        page_id = page["id"]

        response = requests.patch(
            f"{BASE_URL}/pages/{page_id}",
            headers=HEADERS,
            json={
                "in_trash": True
            },
        )

        if not response.ok:

            print()
            print("ERROR trashing page")
            print(
                "Database:",
                database_name
            )
            print(
                "Page ID:",
                page_id
            )
            print(
                "Status:",
                response.status_code
            )
            print(
                "Response:",
                response.text
            )
            print()

            sys.exit(1)

        trashed += 1

        time.sleep(0.1)

    print(
        f"  Trashed {trashed} records."
    )

# ============================================================
# PROPERTY HELPERS
# ============================================================

def title(value):

    return {
        "title": [
            {
                "type": "text",
                "text": {
                    "content": value
                }
            }
        ]
    }


def rich_text(value):

    if not value:
        return {
            "rich_text": []
        }

    return {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": value
                }
            }
        ]
    }


def select(value):

    if not value:
        return {
            "select": None
        }

    return {
        "select": {
            "name": value
        }
    }


def date(value):

    if not value:
        return {
            "date": None
        }

    return {
        "date": {
            "start": value
        }
    }


def relation(page_ids):

    return {
        "relation": [
            {
                "id": page_id
            }
            for page_id in page_ids
        ]
    }


# ============================================================
# CREATE DATABASE PAGE
# ============================================================

def create_database_page(
    data_source_id,
    properties
):

    payload = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": data_source_id,
        },
        "properties": properties,
    }

    return notion_request(
        "POST",
        "/pages",
        payload
    )


# ============================================================
# BUILD TITLE → PAGE ID MAP
# ============================================================

def build_title_map(
    data_source_id,
    title_property
):

    pages = query_data_source(
        data_source_id
    )

    mapping = {}

    for page in pages:

        properties = page.get(
            "properties",
            {}
        )

        prop = properties.get(
            title_property
        )

        if not prop:
            continue

        title_items = prop.get(
            "title",
            []
        )

        if not title_items:
            continue

        name = title_items[0].get(
            "plain_text"
        )

        if name:
            mapping[name] = page["id"]

    return mapping


# ============================================================
# RESOLVE SERVICES
# ============================================================

def resolve_services(
    service_names,
    service_map
):

    resolved = []

    for name in service_names:

        name = name.strip()

        if not name:
            continue

        if name not in service_map:

            print()
            print(
                "ERROR: Service does not exist:"
            )
            print(
                f"  {name}"
            )
            print()
            print(
                "Available services:"
            )

            for service in sorted(
                service_map.keys()
            ):
                print(
                    f"  - {service}"
                )

            print()

            sys.exit(1)

        resolved.append(
            service_map[name]
        )

    return resolved


# ============================================================
# SEED DATA
# ============================================================


# ------------------------------------------------------------
# SERVICES
# ------------------------------------------------------------

SERVICES = [

    ("Microsoft Entra ID", "Identity", "High"),
    ("Azure RBAC", "Identity", "High"),
    ("Management Groups", "Governance", "High"),
    ("Azure Policy", "Governance", "High"),
    ("Azure Resource Manager", "Governance", "High"),
    ("Azure Cost Management", "Governance", "High"),

    ("Azure Storage", "Storage", "High"),
    ("Azure Blob Storage", "Storage", "High"),
    ("Azure Files", "Storage", "High"),
    ("Azure Managed Disks", "Storage", "High"),

    ("Azure Virtual Machines", "Compute", "High"),
    ("VM Scale Sets", "Compute", "High"),
    ("Azure App Service", "Compute", "High"),
    ("Azure Container Instances", "Compute", "Medium"),

    ("Azure Virtual Network", "Networking", "High"),
    ("Network Security Groups", "Networking", "High"),
    ("Azure Route Tables", "Networking", "High"),
    ("Azure DNS", "Networking", "High"),
    ("Azure Load Balancer", "Networking", "High"),
    ("Azure Application Gateway", "Networking", "High"),

    ("Azure Monitor", "Monitoring", "High"),
    ("Log Analytics", "Monitoring", "High"),
    ("Network Watcher", "Monitoring", "High"),

    ("Azure Backup", "Backup", "High"),
    ("Azure Site Recovery", "Backup", "High"),
]


# ------------------------------------------------------------
# KNOWLEDGE
# ------------------------------------------------------------

KNOWLEDGE = [

    ("Azure Resource Hierarchy", "Identity & Governance",
     "Azure Resource Manager"),

    ("Management Groups", "Identity & Governance",
     "Management Groups"),

    ("Subscriptions", "Identity & Governance",
     "Azure Resource Manager"),

    ("Resource Groups", "Identity & Governance",
     "Azure Resource Manager"),

    ("Microsoft Entra Users and Groups", "Identity & Governance",
     "Microsoft Entra ID"),

    ("Azure RBAC", "Identity & Governance",
     "Azure RBAC"),

    ("RBAC Scope", "Identity & Governance",
     "Azure RBAC"),

    ("Azure Policy", "Identity & Governance",
     "Azure Policy"),

    ("Resource Tags", "Identity & Governance",
     "Azure Resource Manager"),

    ("Azure Budgets", "Identity & Governance",
     "Azure Cost Management"),

    ("Storage Account Configuration", "Storage",
     "Azure Storage"),

    ("Blob Storage", "Storage",
     "Azure Blob Storage"),

    ("Azure Files", "Storage",
     "Azure Files"),

    ("Storage Redundancy", "Storage",
     "Azure Storage"),

    ("Shared Access Signatures", "Storage",
     "Azure Storage"),

    ("Storage Lifecycle Management", "Storage",
     "Azure Blob Storage"),

    ("Azure Virtual Machines", "Compute",
     "Azure Virtual Machines"),

    ("Managed Disks", "Compute",
     "Azure Managed Disks"),

    ("Virtual Machine Scale Sets", "Compute",
     "VM Scale Sets"),

    ("Azure App Service", "Compute",
     "Azure App Service"),

    ("Azure Container Instances", "Compute",
     "Azure Container Instances"),

    ("Virtual Networks", "Networking",
     "Azure Virtual Network"),

    ("Subnets", "Networking",
     "Azure Virtual Network"),

    ("Network Security Groups", "Networking",
     "Network Security Groups"),

    ("Route Tables", "Networking",
     "Azure Route Tables"),

    ("VNet Peering", "Networking",
     "Azure Virtual Network"),

    ("Azure DNS", "Networking",
     "Azure DNS"),

    ("Azure Load Balancer", "Networking",
     "Azure Load Balancer"),

    ("Application Gateway", "Networking",
     "Azure Application Gateway"),

    ("Azure Monitor", "Monitoring",
     "Azure Monitor"),

    ("Log Analytics", "Monitoring",
     "Log Analytics"),

    ("Azure Alerts", "Monitoring",
     "Azure Monitor"),

    ("Azure Backup", "Backup & DR",
     "Azure Backup"),

    ("Azure Site Recovery", "Backup & DR",
     "Azure Site Recovery"),
]


# ------------------------------------------------------------
# SERVICE COMPARISONS
# ------------------------------------------------------------

COMPARISONS = [

    (
        "Management Groups vs Subscriptions vs Resource Groups",
        "Governance",
        [
            "Management Groups",
            "Azure Resource Manager",
        ],
        "Where should Azure resources and governance boundaries be organized?",
        "Management groups sit above subscriptions; resource groups sit inside subscriptions.",
        "Do not confuse organizational hierarchy with RBAC scope.",
    ),

    (
        "Azure RBAC vs Azure Policy",
        "Governance",
        [
            "Azure RBAC",
            "Azure Policy",
        ],
        "Do I need to control who can perform an action or what configuration is allowed?",
        "RBAC controls authorization; Policy evaluates and enforces resource configuration and compliance.",
        "Using Policy when the problem is actually permissions.",
    ),

    (
        "Owner vs Contributor vs Reader",
        "Identity",
        [
            "Azure RBAC",
        ],
        "Which built-in RBAC role provides the required level of access?",
        "Owner can manage access; Contributor manages resources but cannot assign RBAC roles; Reader is read-only.",
        "Forgetting that Contributor cannot grant access.",
    ),

    (
        "Blob Storage vs Azure Files",
        "Storage",
        [
            "Azure Blob Storage",
            "Azure Files",
        ],
        "Do I need object storage or a managed file share?",
        "Blob Storage provides object storage; Azure Files provides managed file shares.",
        "Treating Blob Storage like a traditional file share.",
    ),

    (
        "LRS vs ZRS vs GRS vs GZRS",
        "Storage",
        [
            "Azure Storage",
        ],
        "What redundancy model satisfies the availability and geographic requirements?",
        "The models differ in local, zone and geographic replication.",
        "Choosing redundancy based only on price.",
    ),

    (
        "SAS vs Storage Access Key vs Microsoft Entra Authorization",
        "Storage",
        [
            "Azure Storage",
            "Microsoft Entra ID",
        ],
        "How should an application or user authenticate to Storage?",
        "These mechanisms provide different authentication and authorization models.",
        "Using account keys when more constrained authorization is appropriate.",
    ),

    (
        "VM vs VM Scale Set",
        "Compute",
        [
            "Azure Virtual Machines",
            "VM Scale Sets",
        ],
        "Do I need an individual VM or a scalable group of VM instances?",
        "A VM represents an individual compute instance; VMSS manages groups of VMs.",
        "Assuming VMSS is simply a larger VM.",
    ),

    (
        "NSG vs Route Table",
        "Networking",
        [
            "Network Security Groups",
            "Azure Route Tables",
        ],
        "Is the problem traffic filtering or traffic routing?",
        "NSGs filter traffic; route tables determine where traffic is sent.",
        "Trying to solve a routing problem with an NSG.",
    ),

    (
        "Load Balancer vs Application Gateway",
        "Networking",
        [
            "Azure Load Balancer",
            "Azure Application Gateway",
        ],
        "Do I need Layer 4 or Layer 7 load balancing?",
        "Load Balancer operates at Layer 4; Application Gateway provides Layer 7 capabilities.",
        "Choosing based only on the phrase 'load balancing'.",
    ),

    (
        "Azure Monitor vs Log Analytics",
        "Monitoring",
        [
            "Azure Monitor",
            "Log Analytics",
        ],
        "Do I need metrics and alerts or centralized log analysis?",
        "Azure Monitor is the broader monitoring platform; Log Analytics provides log collection and querying.",
        "Treating them as completely separate monitoring systems.",
    ),

    (
        "Azure Backup vs Site Recovery",
        "Backup",
        [
            "Azure Backup",
            "Azure Site Recovery",
        ],
        "Do I need data recovery or disaster recovery/failover?",
        "Backup protects recoverable data; Site Recovery orchestrates replication and recovery.",
        "Using Backup as a replacement for disaster recovery.",
    ),

    (
        "Metrics vs Logs",
        "Monitoring",
        [
            "Azure Monitor",
            "Log Analytics",
        ],
        "Do I need numerical time-series measurements or detailed event/query information?",
        "Metrics are optimized for numerical time-series data; logs provide richer queryable event information.",
        "Assuming every monitoring problem is solved with logs.",
    ),
]


# ------------------------------------------------------------
# SCENARIOS
# ------------------------------------------------------------

SCENARIOS = [

    (
        "Small Enterprise Azure Environment",
        "Integrated",
        "Beginner",
        [
            "Microsoft Entra ID",
            "Azure RBAC",
            "Azure Resource Manager",
            "Azure Storage",
            "Azure Virtual Machines",
            "Azure Virtual Network",
        ],
        "Design and administer a small Azure environment for a 50-person company.",
    ),

    (
        "Medium Enterprise Three-Tier Application",
        "Integrated",
        "Intermediate",
        [
            "Azure Virtual Network",
            "Network Security Groups",
            "Azure Virtual Machines",
            "Azure Load Balancer",
            "Azure Storage",
            "Azure Monitor",
        ],
        "Deploy and operate a three-tier application with separate network segments.",
    ),

    (
        "Hybrid Enterprise Administration",
        "Integrated",
        "Advanced",
        [
            "Microsoft Entra ID",
            "Azure Virtual Network",
            "Azure DNS",
            "Network Security Groups",
            "Azure Monitor",
        ],
        "Administer an Azure environment connected to an on-premises network.",
    ),

    (
        "Broken Production VM",
        "Compute",
        "Intermediate",
        [
            "Azure Virtual Machines",
            "Network Security Groups",
            "Azure Route Tables",
            "Azure Storage",
            "Azure Monitor",
        ],
        "Diagnose a production VM that is running but cannot serve its application.",
    ),

    (
        "Storage Access Incident",
        "Storage",
        "Intermediate",
        [
            "Azure Storage",
            "Azure Blob Storage",
            "Azure RBAC",
        ],
        "Investigate an application that suddenly loses access to blob data.",
    ),

    (
        "Enterprise Monitoring Incident",
        "Monitoring",
        "Advanced",
        [
            "Azure Monitor",
            "Log Analytics",
            "Azure Virtual Machines",
        ],
        "Investigate why production monitoring stopped detecting failures.",
    ),
]


# ------------------------------------------------------------
# TROUBLESHOOTING
# ------------------------------------------------------------

TROUBLESHOOTING = [

    (
        "User receives AuthorizationFailed",
        "User cannot access an Azure resource despite being authenticated.",
        [
            "Azure RBAC",
            "Microsoft Entra ID",
        ],
        "Incorrect RBAC assignment, wrong scope, missing role or deny assignment.",
        "Check identity, role assignment, scope and effective permissions.",
    ),

    (
        "VM cannot connect to another VM",
        "Two VMs exist in Azure but application traffic cannot flow between them.",
        [
            "Azure Virtual Machines",
            "Azure Virtual Network",
            "Network Security Groups",
            "Azure Route Tables",
        ],
        "NSG rule, route, subnet configuration or application listener.",
        "Check effective routes, effective security rules and application connectivity.",
    ),

    (
        "VM has internet access but cannot reach application subnet",
        "Outbound connectivity works but traffic to another subnet fails.",
        [
            "Azure Virtual Network",
            "Network Security Groups",
            "Azure Route Tables",
        ],
        "Incorrect route or NSG rule.",
        "Compare effective routes and effective security rules.",
    ),

    (
        "Blob upload returns authorization error",
        "Application can reach Storage but uploads are denied.",
        [
            "Azure Storage",
            "Azure Blob Storage",
            "Azure RBAC",
        ],
        "Incorrect data-plane authorization, SAS permissions or credentials.",
        "Determine authentication mechanism and inspect effective authorization.",
    ),

    (
        "Log Analytics workspace has no expected data",
        "A resource is running but expected logs are not appearing.",
        [
            "Azure Monitor",
            "Log Analytics",
        ],
        "Diagnostic settings, agent/configuration or query issue.",
        "Verify diagnostic configuration, destination and query.",
    ),

    (
        "Application Gateway backend is unhealthy",
        "Application Gateway is running but backend instances are reported unhealthy.",
        [
            "Azure Application Gateway",
            "Network Security Groups",
            "Azure Virtual Network",
        ],
        "Health probe, backend configuration, NSG or application listener.",
        "Inspect probe configuration and test backend connectivity.",
    ),
]


# ============================================================
# SEED FUNCTIONS
# ============================================================

def seed_services(data_source_id):

    print()
    print("Seeding Services...")

    for (
        service,
        category,
        relevance
    ) in SERVICES:

        properties = {
            "Service": title(service),
            "Category": select(category),
            "Exam Relevance": select(relevance),
        }

        create_database_page(
            data_source_id,
            properties
        )

    print(
        f"  Created {len(SERVICES)} services."
    )


def seed_knowledge(
    data_source_id,
    service_map
):

    print()
    print("Seeding Knowledge...")

    for (
        concept,
        domain,
        service
    ) in KNOWLEDGE:

        properties = {
            "Concept": title(concept),
            "Domain": select(domain),
            "Service": rich_text(service),
        }

        create_database_page(
            data_source_id,
            properties
        )

    print(
        f"  Created {len(KNOWLEDGE)} knowledge records."
    )


def seed_comparisons(
    data_source_id,
    service_map
):

    print()
    print("Seeding Service Comparisons...")

    for (
        comparison,
        category,
        services,
        question,
        difference,
        trap
    ) in COMPARISONS:

        service_ids = resolve_services(
            services,
            service_map
        )

        properties = {
            "Comparison": title(comparison),
            "Category": select(category),
            "Services": relation(service_ids),
            "Decision Question": rich_text(question),
            "Key Difference": rich_text(difference),
            "Exam Trap": rich_text(trap),
        }

        create_database_page(
            data_source_id,
            properties
        )

    print(
        f"  Created {len(COMPARISONS)} comparisons."
    )

def seed_scenarios(
    data_source_id,
    service_map
):

    print()
    print("Seeding Scenarios...")

    for (
        scenario,
        domain,
        difficulty,
        services,
        requirements
    ) in SCENARIOS:

        service_ids = resolve_services(
            services,
            service_map
        )

        properties = {
            "Scenario": title(scenario),
            "Domain": select(domain),
            "Difficulty": select(difficulty),
            "Services": relation(service_ids),
            "Requirements": rich_text(requirements),
            "Status": select("Not Started"),
        }

        create_database_page(
            data_source_id,
            properties
        )

    print(
        f"  Created {len(SCENARIOS)} scenarios."
    )


def seed_troubleshooting(
    data_source_id,
    service_map
):

    print()
    print("Seeding Troubleshooting...")

    for (
        incident,
        symptoms,
        services,
        causes,
        diagnostics
    ) in TROUBLESHOOTING:

        service_ids = resolve_services(
            services,
            service_map
        )

        properties = {
            "Incident": title(incident),
            "Symptoms": rich_text(symptoms),
            "Services": relation(service_ids),
            "Possible Causes": rich_text(causes),
            "Diagnostic Steps": rich_text(diagnostics),
            "Root Cause": rich_text(""),
            "Resolution": rich_text(""),
        }

        create_database_page(
            data_source_id,
            properties
        )

    print(
        f"  Created {len(TROUBLESHOOTING)} "
        f"troubleshooting records."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("==========================================")
    print(" AZ-104 NOTION RESET + SEED")
    print("==========================================")
    print()

    print(
        "WARNING:"
    )
    print(
        "This will DELETE/ARCHIVE all records "
        "from the AZ-104 seed databases."
    )
    print()
    print(
        "The databases themselves will NOT be deleted."
    )
    print()

    answer = input(
        "Type RESET to continue: "
    )

    if answer.strip() != "RESET":

        print()
        print("Cancelled.")
        print()

        sys.exit(0)

    print()
    print("Finding databases...")
    print()

    databases = find_databases()

    print(
        f"Found {len(databases)} child databases."
    )

    print()

    # --------------------------------------------------------
    # Required databases
    # --------------------------------------------------------

    required = [
        "Knowledge",
        "Services",
        "Scenarios",
        "Troubleshooting",
    ]

    for name in required:

        if name not in databases:

            print(
                f"ERROR: Required database missing: "
                f"{name}"
            )

            print()
            print(
                "Run setup_notion.py first."
            )

            sys.exit(1)

    # --------------------------------------------------------
    # Get data source IDs
    # --------------------------------------------------------

    data_sources = {}

    for name, database_id in databases.items():

        print(
            f"Getting data source: {name}"
        )

        data_sources[name] = (
            get_data_source_id(database_id)
        )

    print()

    # --------------------------------------------------------
    # CLEAR SEED DATABASES
    # --------------------------------------------------------

    print("==========================================")
    print(" CLEARING EXISTING DATA")
    print("==========================================")

    clear_names = [
        "Knowledge",
        "Services",
        "Scenarios",
        "Troubleshooting",
    ]

    if "Service Comparisons" in databases:

        clear_names.append(
            "Service Comparisons"
        )

    for name in clear_names:

        clear_data_source(
            data_sources[name],
            name
        )

    print()

    # --------------------------------------------------------
    # SEED SERVICES FIRST
    # --------------------------------------------------------

    seed_services(
        data_sources["Services"]
    )

    # --------------------------------------------------------
    # BUILD SERVICE RELATION MAP
    # --------------------------------------------------------

    print()
    print(
        "Building Service relation map..."
    )

    service_map = build_title_map(
        data_sources["Services"],
        "Service"
    )

    print(
        f"  Found {len(service_map)} services."
    )

    # --------------------------------------------------------
    # KNOWLEDGE
    # --------------------------------------------------------

    seed_knowledge(
        data_sources["Knowledge"],
        service_map
    )

    # --------------------------------------------------------
    # SERVICE COMPARISONS
    # --------------------------------------------------------

    if "Service Comparisons" in databases:

        seed_comparisons(
            data_sources["Service Comparisons"],
            service_map
        )

    else:

        print()
        print(
            "Service Comparisons database not found."
        )
        print(
            "Skipping comparisons."
        )

    # --------------------------------------------------------
    # SCENARIOS
    # --------------------------------------------------------

    seed_scenarios(
        data_sources["Scenarios"],
        service_map
    )

    # --------------------------------------------------------
    # TROUBLESHOOTING
    # --------------------------------------------------------

    seed_troubleshooting(
        data_sources["Troubleshooting"],
        service_map
    )

    # --------------------------------------------------------
    # INTENTIONALLY EMPTY
    # --------------------------------------------------------

    print()
    print("Leaving these databases empty:")
    print("  - Labs")
    print("  - Mistake Log")
    print("  - Mock Tests")
    print("  - Review Queue")

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print()
    print("==========================================")
    print(" AZ-104 RESET + SEED COMPLETE")
    print("==========================================")
    print()

    print(
        f"Services       : {len(SERVICES)}"
    )

    print(
        f"Knowledge      : {len(KNOWLEDGE)}"
    )

    print(
        f"Comparisons    : "
        f"{len(COMPARISONS) if 'Service Comparisons' in databases else 0}"
    )

    print(
        f"Scenarios      : {len(SCENARIOS)}"
    )

    print(
        f"Troubleshooting: {len(TROUBLESHOOTING)}"
    )

    print()
    print(
        "Your AZ-104 knowledge system is ready."
    )
    print()


if __name__ == "__main__":
    main()
