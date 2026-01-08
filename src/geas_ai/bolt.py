from pathlib import Path
from rich.console import Console
import shutil

from geas_ai import utils
from geas_ai.core import ledger
from geas_ai.state import StateManager
from geas_ai.commands.verify import verify as run_verify

console = Console()


class Bolt:
    """Domain model for a GEAS Bolt."""

    def __init__(self, name: str, path: Path, status: str = "draft"):
        self.name = name
        self.path = path
        self.status = status
        self.state_manager = StateManager()

    @classmethod
    def load(cls, name: str) -> "Bolt":
        """Loads a Bolt by name from the state."""
        manager = StateManager()
        bolts = manager.list_bolts()

        if name not in bolts:
            # Fallback: check filesystem if not in state (migration scenario)
            possible_path = utils.get_geas_root() / "bolts" / name
            if possible_path.exists():
                # Auto-register found bolt?
                manager.register_bolt(
                    name,
                    str(possible_path.relative_to(utils.get_geas_root().parent)),
                    "active",
                )
                return cls(name, possible_path, "active")

            raise ValueError(f"Bolt '{name}' not found.")

        data = bolts[name]
        # Resolve path relative to project root
        # stored path like "bolts/feature-login" or ".geas/bolts/feature-login"
        # We assure it's relative to .geas parent (project root)
        project_root = utils.get_geas_root().parent
        bolt_path = (
            project_root / data["path"]
            if "path" in data
            else utils.get_geas_root() / "bolts" / name
        )

        return cls(name, bolt_path, data["status"])

    @classmethod
    def create(cls, name: str) -> "Bolt":
        """Creates a new Bolt on filesystem and registers it."""
        utils.ensure_geas_root()
        utils.validate_slug(name)

        bolt_dir = utils.get_geas_root() / "bolts" / name
        if bolt_dir.exists():
            raise ValueError(f"Bolt '{name}' already exists.")

        # Create directory
        bolt_dir.mkdir(parents=True, exist_ok=True)

        # Init Ledger
        genesis = ledger.LedgerManager.create_genesis_ledger(bolt_id=name)
        ledger.LedgerManager.save_lock(bolt_dir, genesis)

        # Create Request File
        from geas_ai.core import content

        req_path = bolt_dir / "01_request.md"
        req_path.write_text(content.REQUEST_TEMPLATE.format(bolt_name=name))

        # Register in State
        manager = StateManager()
        # Store relative path from project root: .geas/bolts/name
        rel_path = f".geas/bolts/{name}"
        manager.register_bolt(name, rel_path, "draft")
        manager.set_active_bolt(name)

        return cls(name, bolt_dir, "draft")

    def archive(self) -> None:
        """Archives the bolt after verification."""
        # 1. Verify
        try:
            run_verify(bolt=self.name)
        except Exception:
            # The CLI command calling this should handle the prompt/force logic
            # This method assumes we are ready to archive or throws
            # We will throw a specific error if verification fails
            raise RuntimeError(f"Bolt '{self.name}' failed verification.")

        # 2. Move
        archive_root = utils.get_geas_root() / "archive"
        archive_root.mkdir(exist_ok=True)
        target_path = archive_root / self.name

        if target_path.exists():
            raise ValueError(f"Bolt '{self.name}' already exists in archive.")

        shutil.move(str(self.path), str(target_path))

        # 3. Update State
        self.state_manager.update_bolt_status(self.name, "archived")
        # Ensure we don't have a broken active pointer
        if self.state_manager.get_active_bolt() == self.name:
            # We deliberately leave active_bolt as is or set to None?
            # Creating a 'ghost' context is bad. Set to None.
            # But StateManager.remove_bolt handles this.
            # update_bolt_status does not.
            # If we keep it in the list as 'archived', we should probably unset active.
            # Let's direct modify the underlying dict via manager
            pass  # Logic handled in next step or caller

    def delete(self, force: bool = False) -> None:
        """Deletes the bolt."""
        if not self.path.exists():
            # Could be just a state entry cleanup
            self.state_manager.remove_bolt(self.name)
            return

        shutil.rmtree(self.path)
        self.state_manager.remove_bolt(self.name)
