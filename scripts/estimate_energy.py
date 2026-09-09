#!/usr/bin/env python3
"""Reproduce the transparent scenarios in metrics/energy_estimate.json.
No token or provider-infrastructure telemetry is inferred."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def parse_log():
    raw = (ROOT / "metrics/compute_log.jsonl").read_text().replace('\\n', '\n')
    return [json.loads(line) for line in raw.splitlines() if line.strip()]

def main():
    rows = [r for r in parse_log() if "estimation énergétique" not in r.get("phase", "")]
    web = sum(r.get("web_search_calls_approx") or r.get("web_search_batches_approx") or 0 for r in rows)
    tools = sum(r.get("other_tool_calls_approx") or 0 for r in rows)
    batches = 50  # reconstructed; see JSON for rule and uncertainty
    scenarios = {"low": (1, 1.5, 62, .16), "central": (2, 3.91, 187, .31), "high": (5, 7.05, 436, .60)}
    for name, (long_n, long_wh, coord_n, coord_wh) in scenarios.items():
        wh = batches * long_n * long_wh + coord_n * coord_wh
        print(name, f"{wh:.2f} Wh", f"{wh / 1000:.3f} kWh")
    print("logged entries=", len(rows), "web=", web, "tools=", tools)

if __name__ == "__main__":
    main()
