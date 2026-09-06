#!/usr/bin/env python3
"""Validate, update and export the recovered fact-check ledger atomically."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKPOINT = ROOT / "output/checkpoints/registre_revue_factuelle_checkpoint_recupere.json"
DEFAULT_LEDGER = ROOT / "tmp/ledger_restored.json"

ALLOWED_VERDICTS = {
    "Exact",
    "Globalement exact",
    "À nuancer",
    "Trompeur",
    "Faux",
    "Invérifiable ou insuffisamment étayé",
}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    pages = row.get("pdf_pages") or [9999]
    candidates = row.get("candidate_ids") or [""]
    return (pages[0], candidates[0], row.get("id", ""))


def calculate_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [row.get("id") for row in rows]
    duplicate_ids = sorted({claim_id for claim_id in ids if ids.count(claim_id) > 1})
    if None in ids or "" in ids:
        raise ValueError("Every ledger row must have a non-empty id")
    if duplicate_ids:
        raise ValueError(f"Duplicate claim ids: {duplicate_ids}")

    malformed_verified: list[str] = []
    invalid_verdicts: list[tuple[str, Any]] = []
    for row in rows:
        verdict = row.get("verdict")
        if verdict is not None and verdict not in ALLOWED_VERDICTS:
            invalid_verdicts.append((row["id"], verdict))
        if row.get("verification_status") == "vérifiée":
            required = {
                "sources": row.get("sources"),
                "verdict": verdict,
                "justification": row.get("justification"),
                "consensus_or_controversy": row.get("consensus_or_controversy"),
                "source_quality": row.get("source_quality"),
                "confidence": row.get("confidence"),
            }
            if (
                verdict not in ALLOWED_VERDICTS
                or not isinstance(required["sources"], list)
                or len(required["sources"]) == 0
                or any(value in (None, "", "À rétablir") for key, value in required.items() if key != "sources")
            ):
                malformed_verified.append(row["id"])

    if invalid_verdicts:
        raise ValueError(f"Invalid verdicts: {invalid_verdicts}")
    if malformed_verified:
        raise ValueError(f"Verified rows with incomplete evidence fields: {malformed_verified}")

    pending = sorted(
        (row for row in rows if row.get("verification_status") != "vérifiée"),
        key=sort_key,
    )
    verdict_counts: dict[str, int] = {}
    for row in rows:
        key = row.get("verdict") or "PENDING"
        verdict_counts[key] = verdict_counts.get(key, 0) + 1

    return {
        "unique_claims": len(rows),
        "occurrences": sum(len(row.get("occurrences") or []) for row in rows),
        "sourced": sum(bool(row.get("sources")) for row in rows),
        "verified": sum(row.get("verification_status") == "vérifiée" for row in rows),
        "audited": sum(
            (row.get("adversarial_audit_status") or "non audité") != "non audité"
            for row in rows
        ),
        "claims_with_justification": sum(bool(row.get("justification")) for row in rows),
        "first_unfinished": pending[0]["id"] if pending else None,
        "verdict_counts": dict(sorted(verdict_counts.items())),
    }


def refresh_checkpoint(checkpoint: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    for row in rows:
        row.setdefault("needs_sol_review", False)
        row.setdefault("sol_review_reason", None)
    stats = calculate_stats(rows)
    checkpoint["restored_claim_ledger"] = sorted(rows, key=sort_key)
    checkpoint["created_at_utc"] = datetime.now(timezone.utc).isoformat()
    counts = checkpoint.setdefault("recoverable_counts", {})
    counts["structured_claim_rows_reconstructed"] = stats["unique_claims"]
    counts["structured_claim_rows_with_sources_restored"] = stats["sourced"]
    counts["structured_claim_rows_with_verdict_restored"] = stats["verified"]
    counts["structured_claim_rows_adversarially_audited"] = stats["audited"]
    status = checkpoint.setdefault("recovery_status", {})
    status["structured_claim_rows_reconstructed"] = stats["unique_claims"]
    status["structured_occurrences_reconstructed"] = stats["occurrences"]
    checkpoint["active_resume"] = {
        "phase": "fact-checking systématique — sources, verdicts et justifications",
        "first_unfinished_identifier": stats["first_unfinished"],
        "audit_phase_started": stats["audited"] > 0,
    }
    return checkpoint


def apply_changes(checkpoint_path: Path, patch_path: Path, ledger_path: Path) -> dict[str, Any]:
    checkpoint = read_json(checkpoint_path)
    changes = read_json(patch_path)
    rows = copy.deepcopy(checkpoint["restored_claim_ledger"])
    by_id = {row["id"]: row for row in rows}

    for update in changes.get("updates", []):
        claim_id = update["id"]
        if claim_id not in by_id:
            raise KeyError(f"Cannot update unknown claim id {claim_id}")
        by_id[claim_id].update(update.get("set", {}))

    for addition in changes.get("additions", []):
        claim_id = addition.get("id")
        if not claim_id:
            raise ValueError("Every addition must have an id")
        if claim_id in by_id:
            raise ValueError(f"Cannot add existing claim id {claim_id}")
        rows.append(addition)
        by_id[claim_id] = addition

    checkpoint = refresh_checkpoint(checkpoint, rows)
    atomic_json_write(checkpoint_path, checkpoint)
    atomic_json_write(ledger_path, checkpoint["restored_claim_ledger"])

    for artifact in checkpoint.get("artifacts", []):
        if artifact.get("path") == "tmp/ledger_restored.json":
            artifact["size_bytes"] = ledger_path.stat().st_size
            artifact["sha256"] = sha256(ledger_path)
            artifact["modified_at_utc"] = datetime.fromtimestamp(
                ledger_path.stat().st_mtime, tz=timezone.utc
            ).isoformat()
    atomic_json_write(checkpoint_path, checkpoint)
    return calculate_stats(checkpoint["restored_claim_ledger"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("stats")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("patch", type=Path)
    subparsers.add_parser("export")
    args = parser.parse_args()

    checkpoint = read_json(args.checkpoint)
    if args.command == "stats":
        result = calculate_stats(checkpoint["restored_claim_ledger"])
    elif args.command == "export":
        rows = sorted(checkpoint["restored_claim_ledger"], key=sort_key)
        result = calculate_stats(rows)
        atomic_json_write(args.ledger, rows)
    else:
        result = apply_changes(args.checkpoint, args.patch, args.ledger)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
