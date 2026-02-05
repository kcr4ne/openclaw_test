import logging
from typing import List

logger = logging.getLogger("jarvis.core.shield")

from enum import Enum

class ActionStatus(Enum):
    SAFE = "safe"
    APPROVAL_NEEDED = "approval_needed"
    BLOCKED = "blocked"

class SecurityValidator:
    """
    The Iron Dome.
    Intercepts AI actions and blocks anything not in the Allow-list.
    """
    
    def __init__(self):
        # Whitelist of allowed internal action names (not raw shell commands)
        self.ALLOW_LIST = {
            "system_monitor",
            "security_scan_ports",
            "check_firewall",
            "list_processes",
            "read_logs"
        }
        
        # Actions that require explicit user approval (Impact Analysis)
        self.REQUIRE_APPROVAL = {
            "quick_clean",
            "update_system",
            "block_ip",
            "stop_service",
            "delete_file",
            "simulate_attack", # Added for demo
            "resolve_threat",   # Added for demo
            "fix_system_issue"  # Repair logic
        }
        
        self.IMPACTS = {
            "quick_clean": "This will permanently delete files in /tmp and empty the Trash.",
            "update_system": "System packages will be upgraded. This may require a reboot.",
            "block_ip": "This IP will be unable to access any service on this machine.",
            "stop_service": "The selected service will stop immediately. Dependent apps may fail.",
            "delete_file": "This file will be permanently removed. This cannot be undone.",
            "simulate_attack": "⚠️ This will trigger a FAKE High-Priority Security Alert for testing.",
            "resolve_threat": "✅ This will clear all active security alerts.",
            "fix_system_issue": "🔧 This will install missing system keys (GPG) or fix package configurations."
        }

    def validate_action(self, action_name: str) -> ActionStatus:
        """
        Checks if the action is safe to run automatically.
        """
        if action_name in self.ALLOW_LIST:
            return ActionStatus.SAFE
        
        if action_name in self.REQUIRE_APPROVAL:
            logger.warning(f"Action '{action_name}' requires USER APPROVAL.")
            return ActionStatus.APPROVAL_NEEDED
            
        logger.error(f"Action '{action_name}' is BLOCKED (Not in whitelist).")
        return ActionStatus.BLOCKED

    def get_impact_description(self, action_name: str) -> str:
        """
        Returns a human-readable impact description for the UI.
        """
        return self.IMPACTS.get(action_name, "Unknown action. Proceed with extreme caution.")
