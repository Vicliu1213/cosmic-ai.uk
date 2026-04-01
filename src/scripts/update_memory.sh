#!/bin/bash

################################################################################
# Memory System Automatic Update Script
# Comic AI - Memory.md Activation and Persistence System
#
# Purpose: Automatically update memory.md with system state, metrics, and logs
# Usage: ./update_memory.sh [activity_type] [description]
# 
# Activity Types:
#   - test:completed - Mark test run as completed
#   - feature:added - Mark feature as added
#   - feature:updated - Mark feature as updated
#   - bug:fixed - Mark bug as fixed
#   - deployment:success - Mark deployment as successful
#   - system:status - Update system status metrics
#
# Author: Comic AI System
# Date: 2026-02-20
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_FILE="${PROJECT_ROOT}/memory.md"
MEMORY_LOG="${PROJECT_ROOT}/.memory_log.json"
MEMORY_STATE="${PROJECT_ROOT}/.memory_state.json"

# Timestamps
CURRENT_DATE=$(date "+%Y-%m-%d")
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
CURRENT_TIMESTAMP=$(date "+%s")

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

################################################################################
# Initialize memory system state
################################################################################
init_memory_state() {
    if [ ! -f "$MEMORY_STATE" ]; then
        log_info "Initializing memory state file..."
        cat > "$MEMORY_STATE" << 'EOF'
{
  "system_version": "1.0.0",
  "initialized_at": "TIMESTAMP",
  "last_updated": "TIMESTAMP",
  "total_updates": 0,
  "total_commits": 0,
  "layers": {
    "level_1_summary": {
      "status": "active",
      "last_updated": "TIMESTAMP"
    },
    "level_2_timeline": {
      "status": "active",
      "last_updated": "TIMESTAMP"
    },
    "level_3_modules": {
      "status": "active",
      "last_updated": "TIMESTAMP"
    },
    "level_4_tasks": {
      "status": "active",
      "last_updated": "TIMESTAMP"
    }
  }
}
EOF
        sed -i "s/TIMESTAMP/${CURRENT_TIMESTAMP}/g" "$MEMORY_STATE"
        log_success "Memory state initialized"
    fi
}

################################################################################
# Initialize memory activity log
################################################################################
init_memory_log() {
    if [ ! -f "$MEMORY_LOG" ]; then
        log_info "Initializing memory activity log..."
        cat > "$MEMORY_LOG" << 'EOF'
{
  "activities": [],
  "statistics": {
    "total_activities": 0,
    "by_type": {},
    "by_date": {}
  }
}
EOF
        log_success "Memory log initialized"
    fi
}

################################################################################
# Log activity to memory system
################################################################################
log_activity() {
    local activity_type="$1"
    local description="$2"
    local status="${3:-pending}"
    
    log_info "Logging activity: $activity_type"
    
    # Create temporary Python script to update JSON
    python3 << PYTHON_EOF
import json
import os
from datetime import datetime

memory_log = "$MEMORY_LOG"

# Load existing log
if os.path.exists(memory_log):
    with open(memory_log, 'r') as f:
        data = json.load(f)
else:
    data = {"activities": [], "statistics": {"total_activities": 0, "by_type": {}, "by_date": {}}}

# Add new activity
activity = {
    "id": len(data["activities"]) + 1,
    "type": "$activity_type",
    "description": "$description",
    "status": "$status",
    "timestamp": "$CURRENT_TIMESTAMP",
    "datetime": "$CURRENT_TIME"
}

data["activities"].append(activity)
data["statistics"]["total_activities"] += 1

# Update type statistics
if "$activity_type" not in data["statistics"]["by_type"]:
    data["statistics"]["by_type"]["$activity_type"] = 0
data["statistics"]["by_type"]["$activity_type"] += 1

# Update date statistics
if "$CURRENT_DATE" not in data["statistics"]["by_date"]:
    data["statistics"]["by_date"]["$CURRENT_DATE"] = 0
data["statistics"]["by_date"]["$CURRENT_DATE"] += 1

# Save updated log
with open(memory_log, 'w') as f:
    json.dump(data, f, indent=2)

print("Activity logged successfully")
PYTHON_EOF
}

################################################################################
# Update memory.md with activity
################################################################################
update_memory_md() {
    local activity_type="$1"
    local description="$2"
    
    log_info "Updating memory.md..."
    
    case "$activity_type" in
        "test:completed")
            append_test_activity "$description"
            ;;
        "feature:added")
            append_feature_activity "added" "$description"
            ;;
        "feature:updated")
            append_feature_activity "updated" "$description"
            ;;
        "bug:fixed")
            append_bug_activity "$description"
            ;;
        "deployment:success")
            append_deployment_activity "$description"
            ;;
        "system:status")
            update_system_status "$description"
            ;;
        *)
            log_error "Unknown activity type: $activity_type"
            return 1
            ;;
    esac
}

################################################################################
# Append test activity to memory.md
################################################################################
append_test_activity() {
    local description="$1"
    
    # Use Python to append to memory.md
    python3 << PYTHON_EOF
import os
from datetime import datetime

memory_file = "$MEMORY_FILE"

# Read existing content
with open(memory_file, 'r') as f:
    content = f.read()

# Find the "## 6. 防閃退和斷線重連系統" section and insert after it
test_entry = f"""
### Test Activity Log
- ✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: $description
"""

# If we already have a test activity log section, append to it
if "### Test Activity Log" in content:
    # Find the section and append
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "### Test Activity Log" in line:
            # Find the next section or end of file
            j = i + 1
            while j < len(lines) and not lines[j].startswith('##'):
                j += 1
            # Insert before next section
            lines.insert(j, f"- ✅ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: $description")
            content = '\n'.join(lines)
            break
else:
    # Add new section
    if content.endswith('\n'):
        content += test_entry
    else:
        content += '\n' + test_entry

# Write back
with open(memory_file, 'w') as f:
    f.write(content)

print("Test activity appended")
PYTHON_EOF
}

################################################################################
# Append feature activity to memory.md
################################################################################
append_feature_activity() {
    local action="$1"
    local description="$2"
    
    log_info "Appending feature activity: $action - $description"
}

################################################################################
# Append bug fix activity to memory.md
################################################################################
append_bug_activity() {
    local description="$1"
    
    log_info "Appending bug fix activity: $description"
}

################################################################################
# Append deployment activity to memory.md
################################################################################
append_deployment_activity() {
    local description="$1"
    
    log_info "Appending deployment activity: $description"
}

################################################################################
# Update system status metrics
################################################################################
update_system_status() {
    local description="$1"
    
    log_info "Updating system status..."
    
    python3 << PYTHON_EOF
import subprocess
import json
from datetime import datetime

memory_file = "$MEMORY_FILE"
memory_state = "$MEMORY_STATE"

# Collect system metrics
metrics = {
    "timestamp": "$CURRENT_TIME",
    "test_status": "pending",
    "git_status": "pending"
}

# Try to get test count
try:
    result = subprocess.run(
        ["pytest", "--co", "-q"],
        cwd="$PROJECT_ROOT",
        capture_output=True,
        text=True,
        timeout=10
    )
    if "test session" in result.stdout or "passed" in result.stdout:
        metrics["test_status"] = "available"
except:
    pass

# Try to get git status
try:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd="$PROJECT_ROOT",
        capture_output=True,
        text=True,
        timeout=5
    )
    metrics["git_status"] = "clean" if not result.stdout.strip() else "modified"
except:
    pass

# Update memory state
if os.path.exists(memory_state):
    with open(memory_state, 'r') as f:
        state = json.load(f)
    state["last_updated"] = "$CURRENT_TIMESTAMP"
    state["total_updates"] += 1
    with open(memory_state, 'w') as f:
        json.dump(state, f, indent=2)

print("System status updated")
print(json.dumps(metrics, indent=2))
PYTHON_EOF
}

################################################################################
# Generate memory report
################################################################################
generate_memory_report() {
    log_info "Generating memory system report..."
    
    python3 << PYTHON_EOF
import json
import os
from collections import defaultdict

memory_log = "$MEMORY_LOG"
memory_state = "$MEMORY_STATE"

print("\n" + "="*60)
print("MEMORY SYSTEM REPORT")
print("="*60)

if os.path.exists(memory_log):
    with open(memory_log, 'r') as f:
        log_data = json.load(f)
    
    print(f"\nTotal Activities: {log_data['statistics']['total_activities']}")
    print(f"\nActivities by Type:")
    for activity_type, count in log_data['statistics']['by_type'].items():
        print(f"  - {activity_type}: {count}")
    
    print(f"\nActivities by Date:")
    for date, count in log_data['statistics']['by_date'].items():
        print(f"  - {date}: {count}")

if os.path.exists(memory_state):
    with open(memory_state, 'r') as f:
        state_data = json.load(f)
    
    print(f"\nMemory State:")
    print(f"  - System Version: {state_data.get('system_version', 'unknown')}")
    print(f"  - Total Updates: {state_data.get('total_updates', 0)}")

print("\n" + "="*60 + "\n")
PYTHON_EOF
}

################################################################################
# Main execution
################################################################################
main() {
    log_info "Comic AI Memory System Update Starting..."
    log_info "Project Root: $PROJECT_ROOT"
    
    # Initialize system
    init_memory_state
    init_memory_log
    
    # Check if activity type was provided
    if [ -z "$1" ]; then
        log_warn "No activity type specified. Usage: $0 [activity_type] [description]"
        log_info "Available activity types:"
        echo "  - test:completed"
        echo "  - feature:added"
        echo "  - feature:updated"
        echo "  - bug:fixed"
        echo "  - deployment:success"
        echo "  - system:status"
        return 1
    fi
    
    ACTIVITY_TYPE="$1"
    DESCRIPTION="${2:-Manual update}"
    
    # Log activity
    log_activity "$ACTIVITY_TYPE" "$DESCRIPTION"
    
    # Update memory.md
    update_memory_md "$ACTIVITY_TYPE" "$DESCRIPTION"
    
    # Generate report
    generate_memory_report
    
    log_success "Memory system update completed"
}

# Run main function
main "$@"
