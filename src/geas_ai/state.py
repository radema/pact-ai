import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, cast
from rich.console import Console
from geas_ai import utils

console = Console()

STATE_FILE_NAME = "state.json"
ACTIVE_CONTEXT_FILE = "active_context.md"  # Deprecated but maintained for compatibility


class StateManager:
    """Manages the global GEAS state in .geas/state.json."""

    def __init__(self, root_path: Optional[Path] = None):
        self.root = root_path or utils.get_geas_root()
        self.state_path = self.root / STATE_FILE_NAME
        self.context_path = self.root / ACTIVE_CONTEXT_FILE
        self._ensure_state_exists()

    def _ensure_state_exists(self) -> None:
        """Creates the state file if it doesn't exist."""
        if not self.state_path.exists():
            self._save_state(
                {
                    "version": "1.0",
                    "active_bolt": None,
                    "last_updated": datetime.utcnow().isoformat(),
                    "bolts": {},
                }
            )

    def _load_state(self) -> Dict[str, Any]:
        """Loads state from JSON file."""
        try:
            with open(self.state_path, "r") as f:
                return cast(Dict[str, Any], json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"version": "1.0", "active_bolt": None, "bolts": {}}

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Saves state to JSON file."""
        state["last_updated"] = datetime.utcnow().isoformat()
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2)

        # Maintain backward compatibility
        self._sync_active_context(state)

    def _sync_active_context(self, state: Dict[str, Any]) -> None:
        """Updates the legacy active_context.md file."""
        active_bolt = state.get("active_bolt")
        if not active_bolt:
            return

        bolt_data = state.get("bolts", {}).get(active_bolt)
        if not bolt_data:
            return

        # Simple template recreation - imports avoided to prevent circular deps if possible
        # But we need basic content
        timestamp = state.get("last_updated", "")
        path = bolt_data.get("path", f".geas/bolts/{active_bolt}")

        content = f"""# Active Context

**Current Bolt:** {active_bolt}
**Path:** {path}
**Started:** {timestamp}

## Instructions for Agent
You are currently working on the Bolt listed above.
1. Read the `01_request.md` in the target directory.
2. If strictly following GEAS, do not edit code until `03_plan.md` is sealed.
"""
        with open(self.context_path, "w") as f:
            f.write(content)

    def get_active_bolt(self) -> Optional[str]:
        """Returns the name of the active bolt."""
        state = self._load_state()
        return state.get("active_bolt")

    def set_active_bolt(self, name: Optional[str]) -> None:
        """Sets the active bolt. Must be a registered bolt or None to clear."""
        state = self._load_state()
        if name is not None and name not in state.get("bolts", {}):
            raise ValueError(f"Bolt '{name}' is not registered in state.")

        state["active_bolt"] = name
        self._save_state(state)

    def register_bolt(self, name: str, path: str, status: str = "draft") -> None:
        """Registers a new bolt in the state."""
        state = self._load_state()
        state["bolts"][name] = {
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "path": path,
        }
        # Auto-set active if none exists? Or usually explicit checkout.
        # But 'geas new' usually switches context.
        # We'll leave that to the caller logic.
        self._save_state(state)

    def update_bolt_status(self, name: str, status: str) -> None:
        """Updates the status of an existing bolt."""
        state = self._load_state()
        if name in state.get("bolts", {}):
            state["bolts"][name]["status"] = status
            self._save_state(state)

    def remove_bolt(self, name: str) -> None:
        """Removes a bolt from state."""
        state = self._load_state()
        if name in state.get("bolts", {}):
            del state["bolts"][name]

        if state.get("active_bolt") == name:
            state["active_bolt"] = None

        self._save_state(state)

    def list_bolts(self) -> Dict[str, Dict[str, Any]]:
        """Returns the dictionary of bolts."""
        state = self._load_state()
        return cast(Dict[str, Dict[str, Any]], state.get("bolts", {}))
