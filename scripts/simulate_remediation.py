from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "outputs" / "incident_events.json"
OUTPUT = ROOT / "outputs" / "remediation_simulation.md"
if not INPUT.exists():
    raise FileNotFoundError("Run scripts/triage_from_day3.py first.")
payload = json.loads(INPUT.read_text(encoding="utf-8"))
lines = [
    "# Remediation Simulation — NO SIDE EFFECTS",
    "",
    "This is a training simulation. No server, cloud API, service, or production system was contacted or changed.",
    "",
    f"Day 3 observations flagged: {payload['flagged_observations']}",
    "",
    "## Simulated decision log",
]
if not payload["incidents"]:
    lines.append("No observations were flagged; no remediation would be considered.")
for event in payload["incidents"]:
    lines += [
        f"### {event['incident_id']} ({event['severity']})",
        f"- Host: {event['host']} at {event['timestamp']}",
        "- Proposed safe next action: collect read-only diagnostics and validate impact.",
        "- Required before any real remediation: confirmed diagnosis, authorized owner, approved change/incident process, and rollback plan.",
        "- Action performed by this simulation: none.",
        "",
    ]
OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote simulation report: {OUTPUT}")
print("No real remediation was performed.")
