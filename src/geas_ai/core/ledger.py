import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from geas_ai.schemas.ledger import Ledger, LedgerEvent, LedgerAction
from geas_ai.core.hashing import calculate_event_hash
from geas_ai.utils import get_active_bolt_name

LOCK_FILE_NAME = "lock.json"

class LedgerIntegrityError(Exception):
    """Raised when ledger chain verification fails."""
    pass

class LedgerManager:
    """Manages lock.json operations."""

    @staticmethod
    def load_lock(bolt_path: Path) -> Optional[Ledger]:
        """Loads the ledger from lock.json if it exists."""
        lock_path = bolt_path / LOCK_FILE_NAME
        if not lock_path.exists():
            return None

        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Ledger(**data)
        except Exception:
            # If load fails (e.g. empty or corrupted), we treat as None or raise
            # For now, let's raise to indicate corruption
            raise

    @staticmethod
    def save_lock(bolt_path: Path, ledger: Ledger) -> None:
        """Saves the ledger to lock.json."""
        lock_path = bolt_path / LOCK_FILE_NAME
        with open(lock_path, "w", encoding="utf-8") as f:
            f.write(ledger.model_dump_json(indent=2))

    @staticmethod
    def create_genesis_ledger(bolt_id: str) -> Ledger:
        """Creates a new empty ledger."""
        return Ledger(
            bolt_id=bolt_id,
            created_at=datetime.utcnow(),
            events=[]
        )

    @staticmethod
    def append_event(ledger: Ledger, event_data: LedgerEvent) -> Ledger:
        """
        Appends a new event to the ledger.
        Updates sequence, prev_hash, and calculates event_hash.
        Note: The input event_data should have action, payload, identity set.
        Sequence, timestamp, prev_hash, event_hash will be handled here if not set correctly,
        but for strictness we expect caller to prepare most of it,
        EXCEPT hashing and linking which MUST be done here to ensure consistency.

        However, to simplify usage: we will take a partially constructed event
        or arguments and build the final event here.

        Let's assume the caller constructs a LedgerEvent BUT we override
        sequence, prev_hash, and event_hash to ensure integrity.
        """

        # 1. Determine Sequence
        new_sequence = len(ledger.events) + 1

        # 2. Get Prev Hash
        prev_hash = ledger.head_hash

        # 3. Update Event fields
        event_data.sequence = new_sequence
        event_data.prev_hash = prev_hash

        # 4. Calculate Event Hash
        # Convert to dict, exclude 'event_hash' for calculation
        event_dict = event_data.model_dump(mode='json')
        if 'event_hash' in event_dict:
            del event_dict['event_hash']

        event_hash = calculate_event_hash(event_dict)
        event_data.event_hash = event_hash

        # 5. Append and Update Head
        ledger.events.append(event_data)
        ledger.head_hash = event_hash

        return ledger

    @staticmethod
    def verify_chain_integrity(ledger: Ledger) -> bool:
        """
        Verifies the hash chain integrity of the ledger.
        """
        current_prev_hash = None

        for i, event in enumerate(ledger.events):
            # Check sequence
            if event.sequence != i + 1:
                return False

            # Check prev_hash linking
            if event.prev_hash != current_prev_hash:
                return False

            # Check event hash
            event_dict = event.model_dump(mode='json')
            if 'event_hash' in event_dict:
                del event_dict['event_hash']

            calculated_hash = calculate_event_hash(event_dict)
            if calculated_hash != event.event_hash:
                return False

            current_prev_hash = event.event_hash

        # Check head hash matches last event
        if ledger.events and ledger.head_hash != ledger.events[-1].event_hash:
            return False

        return True
