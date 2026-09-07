#!/usr/bin/env python3
"""Materialize a fetch-friendly report payload from the authoritative checkpoint.

This script is deliberately standard-library-only so it can run in GitHub Actions.
It decodes the Base64-encoded XZ checkpoint referenced by checkpoints/latest.json,
validates the verified subset, computes descriptive statistics, and writes the
verified rows in small JSON chunks that are easy to retrieve through connectors.
"""

from __future__ import annotations

import base64
import json
import lzma
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "checkpoints" / "latest.json"
OUT = ROOT / "analysis" / "interim_415"
CHUNK_SIZE = 10
ALLOWED_VERDICTS = [
    "Exact",
    "Globalement exact",
    "À nuancer",
    "Trompeur",
    "Faux",
    "Invérifiable ou insuffisamment étayé",
]


def load_authoritative_checkpoint() -> tuple[dict[str, Any], dict[str, Any], Path]:
    latest = json.loads(LATEST.read_text(encoding="utf-8"))
    name = latest["authoritative_recovery_source"]["name"]
    path = ROOT / "checkpoints" / name
    raw = path.read_text(encoding="utf-8")
    compressed = base64.b64decode(raw)
    payload = lzma.decompress(compressed)
    expected = latest["authoritative_recovery_source"].get("uncompressed_sha256")
    if expected:
        import hashlib
        actual = hashlib.sha256(payload).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Uncompressed checkpoint SHA mismatch: {actual} != {expected}")
    return latest, json.loads(payload), path


def nonempty(value: Any) -> bool:
    return value not in (None, "", [], {}, "À rétablir")


def scalar_label(value: Any) -> str:
    if value is None or value == "":
        return "Non renseigné"
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return "; ".join(str(x) for x in value) if value else "Non renseigné"
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def main() -> None:
    latest, checkpoint, checkpoint_path = load_authoritative_checkpoint()
    rows = checkpoint.get("restored_claim_ledger")
    if not isinstance(rows, list):
        raise RuntimeError("Authoritative checkpoint has no restored_claim_ledger list")

    verified = [r for r in rows if r.get("verification_status") == "vérifiée"]
    pending = [r for r in rows if r.get("verification_status") != "vérifiée"]

    malformed: list[dict[str, Any]] = []
    duplicate_ids = [k for k, v in Counter(r.get("id") for r in rows).items() if v > 1]
    for r in verified:
        missing = []
        for field in ("sources", "verdict", "justification", "consensus_or_controversy", "source_quality", "confidence"):
            if not nonempty(r.get(field)):
                missing.append(field)
        if r.get("verdict") not in ALLOWED_VERDICTS:
            missing.append("valid_verdict")
        if missing:
            malformed.append({"id": r.get("id"), "missing_or_invalid": missing})

    verdict_counts = Counter(r.get("verdict") or "PENDING" for r in verified)
    total_verified = len(verified)

    def grouped(field: str) -> list[dict[str, Any]]:
        groups: dict[str, Counter[str]] = defaultdict(Counter)
        totals = Counter()
        for r in verified:
            label = scalar_label(r.get(field))
            groups[label][r.get("verdict") or "PENDING"] += 1
            totals[label] += 1
        out = []
        for label, n in totals.most_common():
            out.append({
                field: label,
                "n": n,
                "verdict_counts": dict(groups[label]),
            })
        return out

    field_presence = {}
    all_fields = sorted({k for r in rows for k in r})
    for field in all_fields:
        field_presence[field] = {
            "verified_nonempty": sum(nonempty(r.get(field)) for r in verified),
            "verified_total": total_verified,
        }

    sol_review = [r for r in verified if r.get("needs_sol_review") is True]
    confidence_counts = Counter(scalar_label(r.get("confidence")) for r in verified)
    source_quality_counts = Counter(scalar_label(r.get("source_quality")) for r in verified)
    type_counts = Counter(scalar_label(r.get("claim_type")) for r in verified)

    occurrence_count = sum(len(r.get("occurrences") or []) for r in rows)
    verified_occurrences = sum(len(r.get("occurrences") or []) for r in verified)

    stats = {
        "generated_from": {
            "latest_json_timestamp_utc": latest.get("timestamp_utc"),
            "authoritative_checkpoint": checkpoint_path.name,
            "phase": latest.get("phase"),
        },
        "corpus": {
            "source_pdf_pages": latest.get("source_pdf_pages"),
            "chapters_covered": latest.get("chapters_covered"),
            "automatic_candidates_extracted": latest.get("counters", {}).get("automatic_candidates_extracted"),
            "unique_claims_total": len(rows),
            "occurrences_total": occurrence_count,
            "verified_claims": total_verified,
            "verified_occurrences": verified_occurrences,
            "pending_claims": len(pending),
            "coverage_percent": round(total_verified / len(rows) * 100, 2) if rows else 0,
            "first_unfinished_identifier": latest.get("resume", {}).get("first_unfinished_identifier"),
        },
        "verdicts": [
            {
                "verdict": verdict,
                "n": verdict_counts.get(verdict, 0),
                "percent_of_verified": round(verdict_counts.get(verdict, 0) / total_verified * 100, 2) if total_verified else 0,
            }
            for verdict in ALLOWED_VERDICTS
        ],
        "needs_sol_review": {
            "n": len(sol_review),
            "ids": [r.get("id") for r in sol_review],
            "reasons": {r.get("id"): r.get("sol_review_reason") for r in sol_review},
        },
        "confidence_counts": dict(confidence_counts),
        "source_quality_counts": dict(source_quality_counts),
        "claim_type_counts": dict(type_counts),
        "by_chapter": grouped("chapter"),
        "by_claim_type": grouped("claim_type"),
        "field_presence": field_presence,
    }

    qa = {
        "duplicate_ids": duplicate_ids,
        "malformed_verified_rows": malformed,
        "latest_counter_verified": latest.get("counters", {}).get("claims_verified"),
        "actual_verified": total_verified,
        "latest_counter_unique": latest.get("counters", {}).get("unique_claims_consolidated"),
        "actual_unique": len(rows),
        "latest_counter_occurrences": latest.get("counters", {}).get("occurrences"),
        "actual_occurrences": occurrence_count,
        "counter_consistent": (
            latest.get("counters", {}).get("claims_verified") == total_verified
            and latest.get("counters", {}).get("unique_claims_consolidated") == len(rows)
            and latest.get("counters", {}).get("occurrences") == occurrence_count
        ),
        "report_ready_subset": not duplicate_ids and not malformed,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("claims_*.json"):
        old.unlink()
    (OUT / "statistics.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "quality_control.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "field_names.json").write_text(json.dumps(all_fields, ensure_ascii=False, indent=2), encoding="utf-8")

    index = []
    for i in range(0, total_verified, CHUNK_SIZE):
        chunk = verified[i:i+CHUNK_SIZE]
        name = f"claims_{i//CHUNK_SIZE + 1:03d}.json"
        (OUT / name).write_text(json.dumps(chunk, ensure_ascii=False, indent=2), encoding="utf-8")
        index.append({
            "file": name,
            "start_index": i + 1,
            "end_index": i + len(chunk),
            "ids": [r.get("id") for r in chunk],
        })
    (OUT / "claims_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    # Small editorial payload: enough for report structure and reproducibility notes.
    editorial = {
        "title": f"Revue factuelle du programme des Écologistes 2026 — rapport sur {total_verified} affirmations vérifiées",
        "scope_note": (
            f"Le corpus consolidé comprend {len(rows)} affirmations uniques. Cette version du rapport porte sur "
            f"les {total_verified} affirmations déjà vérifiées ({round(total_verified/len(rows)*100, 1)} %). "
            "Les affirmations restantes n'entrent pas dans les statistiques de verdict de cette version."
        ),
        "limitations": [
            "Le sous-corpus vérifié correspond à l'avancement séquentiel de la passe primaire et n'est pas un échantillon aléatoire du programme.",
            "Aucun audit contradictoire exhaustif n'a été réalisé pour cette version intermédiaire.",
            "Les conclusions ne doivent pas être extrapolées mécaniquement aux affirmations encore non vérifiées.",
        ],
    }
    (OUT / "editorial.json").write_text(json.dumps(editorial, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"verified": total_verified, "chunks": len(index), "qa": qa}, ensure_ascii=False))


if __name__ == "__main__":
    main()
