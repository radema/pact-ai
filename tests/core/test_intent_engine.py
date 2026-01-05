from datetime import datetime
from geas_ai.core import hashing, ledger
from geas_ai.schemas.ledger import LedgerEvent, LedgerAction


def test_canonicalize_json():
    data = {"b": 2, "a": 1}
    # Expected: {"a":1,"b":2} (no spaces, sorted keys)
    expected = b'{"a":1,"b":2}'
    assert hashing.canonicalize_json(data) == expected


def test_calculate_event_hash():
    event_data = {"sequence": 1, "action": "SEAL_REQ", "payload": {"foo": "bar"}}
    h = hashing.calculate_event_hash(event_data)
    assert h.startswith("sha256:")


def test_ledger_integrity():
    # 1. Create Ledger
    l = ledger.LedgerManager.create_genesis_ledger("test-bolt")  # noqa: E741
    assert l.head_hash is None
    assert len(l.events) == 0

    # 2. Add Event 1
    ev1 = LedgerEvent(
        sequence=0,
        timestamp=datetime.utcnow(),
        action=LedgerAction.SEAL_REQ,
        payload={"data": "1"},
        event_hash="",
    )
    ledger.LedgerManager.append_event(l, ev1)

    assert l.events[0].sequence == 1
    assert l.events[0].prev_hash is None
    assert l.head_hash == l.events[0].event_hash

    # 3. Add Event 2
    ev2 = LedgerEvent(
        sequence=0,
        timestamp=datetime.utcnow(),
        action=LedgerAction.SEAL_SPECS,
        payload={"data": "2"},
        event_hash="",
    )
    ledger.LedgerManager.append_event(l, ev2)

    assert l.events[1].sequence == 2
    assert l.events[1].prev_hash == l.events[0].event_hash
    assert l.head_hash == l.events[1].event_hash

    # 4. Verify Integrity
    assert ledger.LedgerManager.verify_chain_integrity(l) is True

    # 5. Break Integrity (Tamper)
    l.events[0].payload["data"] = "tampered"
    assert ledger.LedgerManager.verify_chain_integrity(l) is False
