#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# AZ-104 Repository Structure Bootstrap Script
# ============================================================
#
# Purpose:
#   Creates the complete AZ-104 repository folder structure,
#   including all labs and standard lab subfolders.
#
# Safe to run multiple times.
#
# Usage from GitHub Codespaces:
#
#   chmod +x scripts/setup-repo-structure.sh
#   ./scripts/setup-repo-structure.sh
#
# ============================================================


# ------------------------------------------------------------
# Repository root
# ------------------------------------------------------------

REPO_ROOT="."


# ------------------------------------------------------------
# Top-level AZ-104 repository structure
# ------------------------------------------------------------

echo "=========================================="
echo " AZ-104 Repository Structure Setup"
echo "=========================================="
echo

echo "Creating top-level repository structure..."

mkdir -p \
    labs \
    scenarios \
    bicep \
    cli \
    powershell \
    scripts \
    troubleshooting \
    mock-tests

touch README.md


# ------------------------------------------------------------
# Lab definitions
# ------------------------------------------------------------

LABS=(
    # 01 - Identities and Governance
    "01-identities-and-governance/01-entra-users-groups"
    "01-identities-and-governance/02-rbac"
    "01-identities-and-governance/03-azure-policy"
    "01-identities-and-governance/04-subscriptions-and-management-groups"
    "01-identities-and-governance/05-resource-locks"
    "01-identities-and-governance/06-tags-and-cost-management"

    # 02 - Storage
    "02-storage/01-storage-accounts"
    "02-storage/02-blob-storage"
    "02-storage/03-file-storage"
    "02-storage/04-storage-security"
    "02-storage/05-storage-replication"
    "02-storage/06-lifecycle-management"

    # 03 - Compute
    "03-compute/01-vms"
    "03-compute/02-vm-disks"
    "03-compute/03-vm-availability"
    "03-compute/04-vmss"
    "03-compute/05-app-service"
    "03-compute/06-containers"

    # 04 - Networking
    "04-networking/01-vnets-and-subnets"
    "04-networking/02-nsgs"
    "04-networking/03-routing"
    "04-networking/04-vnet-peering"
    "04-networking/05-public-and-private-endpoints"
    "04-networking/06-dns"
    "04-networking/07-load-balancing"
    "04-networking/08-application-gateway"

    # 05 - Monitoring and Management
    "05-monitoring-and-management/01-azure-monitor"
    "05-monitoring-and-management/02-log-analytics"
    "05-monitoring-and-management/03-alerts"
    "05-monitoring-and-management/04-action-groups"
    "05-monitoring-and-management/05-network-watcher"
    "05-monitoring-and-management/06-resource-health"
    "05-monitoring-and-management/07-activity-log"

    # 06 - Backup and Business Continuity
    "06-backup-and-business-continuity/01-recovery-services-vault"
    "06-backup-and-business-continuity/02-azure-backup"
    "06-backup-and-business-continuity/03-site-recovery"
    "06-backup-and-business-continuity/04-vm-backup-and-restore"

    # 07 - Integrated Scenarios
    "07-integrated-scenarios/01-small-business"
    "07-integrated-scenarios/02-medium-enterprise"
    "07-integrated-scenarios/03-hybrid-enterprise"
    "07-integrated-scenarios/04-secure-web-application"
    "07-integrated-scenarios/05-troubleshooting-day"
)


# ------------------------------------------------------------
# Create lab structure
# ------------------------------------------------------------

echo
echo "Creating AZ-104 lab structure..."
echo

for lab in "${LABS[@]}"; do

    LAB_PATH="labs/$lab"

    echo "Creating: $LAB_PATH"

    mkdir -p \
        "$LAB_PATH/bicep" \
        "$LAB_PATH/scripts" \
        "$LAB_PATH/validation" \
        "$LAB_PATH/cleanup"

    # README for the individual lab
    touch "$LAB_PATH/README.md"

    # Keep empty directories tracked by Git
    touch "$LAB_PATH/bicep/.gitkeep"
    touch "$LAB_PATH/scripts/.gitkeep"
    touch "$LAB_PATH/validation/.gitkeep"
    touch "$LAB_PATH/cleanup/.gitkeep"

done


# ------------------------------------------------------------
# Git tracking files for top-level empty directories
# ------------------------------------------------------------

echo
echo "Creating .gitkeep files for empty top-level directories..."

touch \
    labs/.gitkeep \
    scenarios/.gitkeep \
    bicep/.gitkeep \
    cli/.gitkeep \
    powershell/.gitkeep \
    scripts/.gitkeep \
    troubleshooting/.gitkeep \
    mock-tests/.gitkeep


# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

echo
echo "=========================================="
echo " AZ-104 structure created successfully"
echo "=========================================="
echo

echo "Top-level directories:"
echo

find . -maxdepth 1 -type d | sort

echo
echo "Number of labs: ${#LABS[@]}"

echo
echo "Lab structure:"
echo

find labs -maxdepth 3 -type d | sort

echo
echo "=========================================="
echo " Done"
echo "=========================================="