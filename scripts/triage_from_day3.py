from pathlib import Path
import csv
import json
from incident_logic import load_day3_output, build_incidents

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "day3" / "anomaly_comparison.csv"
OUTPUT_DIR = ROOT / "outputs"
JSON_OUT = OUTPUT_DIR / "incident_events.json"
REPORT_OUT = OUTPUT_DIR / "day4_incident_report.md"

rows = load_day3_output(INPUT)
incidents = build_incidents(rows)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

payload = {
    "source_file": "data/day3/anomaly_comparison.csv",
    "total_observations": len(rows),
    "flagged_observations": len(incidents),
    "note": "Training classification only; not a confirmed incident or root cause.",
    "incidents": incidents,
}
JSON_OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

lines = [
    "# Day 4 Incident Triage Report",
    "",
    "> Source: Day 3 `anomaly_comparison.csv`. Synthetic training data only.",
    "",
    "## Summary",
    f"- Observations read: {len(rows)}",
    f"- Observations flagged by at least one Day 3 detector: {len(incidents)}",
    f"- HIGH/CRITICAL issues recommended for creation: {sum(1 for i in incidents if i['create_issue'])}",
    "",
    "## Flagged observations",
]
if not incidents:
    lines.append("No observations were flagged by either Day 3 detector. No incident ticket is recommended.")
for inc in incidents:
    lines += [
        f"### {inc['incident_id']} — {inc['severity']}",
        f"- Timestamp: `{inc['timestamp']}`",
        f"- Host: `{inc['host']}`",
        f"- CPU: {inc['cpu_percent']:.1f}%",
        f"- Memory: {inc['memory_percent']:.1f}%",
        f"- Response time: {inc['response_time_ms']:.0f} ms",
        f"- HTTP 5xx errors: {inc['http_5xx_count']:.0f} per observation interval",
        f"- Detected by: {', '.join(inc['detected_by'])}",
        f"- Metric signals: {', '.join(inc['metric_reasons']) if inc['metric_reasons'] else 'No configured metric reason recorded'}",
        f"- Create GitHub Issue: {inc['create_issue']}",
        "",
    ]
lines += [
    "## Recommended next checks (read-only first)",
    "1. Review application logs for each flagged host and time window.",
    "2. Check request volume, endpoint latency, and error rates.",
    "3. Compare deployment or configuration events in the same time window.",
    "4. Inspect host/container and dependency/database health metrics.",
    "5. Follow the organization's incident and escalation process.",
    "",
    "## Safety and limits",
    "- Day 3 detector flags are investigation candidates, not proof of an incident.",
    "- Training severity rules are illustrative and must be agreed with service owners before production use.",
    "- This report does not establish root cause or customer impact.",
    "- No command is run against a real server; no production change is authorized.",
]
REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("DAY 4 TRIAGE GENERATED FROM DAY 3 OUTPUT")
print(f"Observations read: {len(rows)}")
print(f"Flagged observations: {len(incidents)}")
for inc in incidents:
    print(f"{inc['timestamp']} | {inc['host']} | {inc['severity']} | issue={inc['create_issue']}")
print(f"Report: {REPORT_OUT}")
print(f"Incident event JSON (generated): {JSON_OUT}")
