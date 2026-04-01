
# internal/pkg/audit.py
import logging
import json
from datetime import datetime

audit_logger = logging.getLogger("audit")

def log_action(user_id: str, action: str, details: dict):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "details": details
    }
    audit_logger.info(json.dumps(entry))
