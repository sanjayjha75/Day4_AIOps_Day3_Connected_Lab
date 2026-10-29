"""Day 4 logic that consumes Day 3 anomaly_comparison.csv."""
from __future__ import annotations
import csv
import re
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = [
    "timestamp", "host", "cpu_percent", "memory_percent",
    "response_time_ms", "http_5xx_count", "rule_anomaly",
    "ml_anomaly", "reference_flag", "investigation_reason",
]
NUMERIC_COLUMNS = ["cpu_percent", "memory_percent", "response_time_ms", "http_5xx_count"]
FLAG_COLUMNS = ["rule_anomaly", "ml_anomaly", "reference_flag"]

class Day3OutputError(ValueError):
    """Raised when the Day 3 CSV does not match the expected schema or values."""

def load_day3_output(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Day 3 output not found: {path}\n"
            "Copy Day 3 data/processed/anomaly_comparison.csv to Day 4 data/day3/anomaly_comparison.csv."
        )
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise Day3OutputError("Input CSV has no header row.")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise Day3OutputError(f"Missing required columns: {missing}. Use the Day 3 anomaly_comparison.csv output.")
        rows = list(reader)
    if not rows:
        raise Day3OutputError("The Day 3 comparison CSV contains no observations.")
    clean = []
    for i, row in enumerate(rows, start=2):
        if not row.get("timestamp", "").strip() or not row.get("host", "").strip():
            raise Day3OutputError(f"Row {i}: timestamp and host must not be empty.")
        parsed = dict(row)
        for col in NUMERIC_COLUMNS:
            try:
                parsed[col] = float(row[col])
            except (ValueError, TypeError):
                raise Day3OutputError(f"Row {i}: '{col}' must be numeric; received {row.get(col)!r}.")
        for col in FLAG_COLUMNS:
            try:
                value = int(row[col])
            except (ValueError, TypeError):
                raise Day3OutputError(f"Row {i}: '{col}' must be 0 or 1; received {row.get(col)!r}.")
            if value not in (0, 1):
                raise Day3OutputError(f"Row {i}: '{col}' must be 0 or 1; received {value}.")
            parsed[col] = value
        if not 0 <= parsed["cpu_percent"] <= 100:
            raise Day3OutputError(f"Row {i}: cpu_percent must be between 0 and 100.")
        if not 0 <= parsed["memory_percent"] <= 100:
            raise Day3OutputError(f"Row {i}: memory_percent must be between 0 and 100.")
        if parsed["response_time_ms"] < 0 or parsed["http_5xx_count"] < 0:
            raise Day3OutputError(f"Row {i}: response time and HTTP error count cannot be negative.")
        clean.append(parsed)
    return clean

def classify_observation(row: dict[str, Any]) -> dict[str, Any] | None:
    """Turn one row flagged by Day 3 into a Day 4 triage record.

    The rules below are training rules only. They do not confirm an actual incident.
    """
    rule_flag = int(row["rule_anomaly"])
    ml_flag = int(row["ml_anomaly"])
    if not (rule_flag or ml_flag):
        return None
    cpu = float(row["cpu_percent"])
    memory = float(row["memory_percent"])
    latency = float(row["response_time_ms"])
    errors = float(row["http_5xx_count"])
    critical_pattern = cpu >= 95 and latency >= 1000 and errors >= 20
    if critical_pattern:
        severity = "CRITICAL"
    elif rule_flag and ml_flag:
        severity = "HIGH"
    else:
        severity = "MEDIUM"
    digits = re.sub(r"[^0-9]", "", str(row["timestamp"]))[:14]
    host_slug = re.sub(r"[^A-Za-z0-9-]", "-", str(row["host"])).strip("-").lower()
    incident_id = f"INC-{digits}-{host_slug}"
    metric_reasons = []
    if cpu > 90: metric_reasons.append("CPU > 90%")
    if memory > 90: metric_reasons.append("memory > 90%")
    if latency > 1000: metric_reasons.append("response time > 1000 ms")
    if errors > 5: metric_reasons.append("HTTP 5xx count > 5")
    detector_names = []
    if rule_flag: detector_names.append("rule-based detector")
    if ml_flag: detector_names.append("Isolation Forest")
    issue_title = f"AIOps triage {incident_id} - {severity}"
    return {
        "incident_id": incident_id,
        "timestamp": str(row["timestamp"]),
        "host": str(row["host"]),
        "cpu_percent": cpu,
        "memory_percent": memory,
        "response_time_ms": latency,
        "http_5xx_count": errors,
        "rule_anomaly": rule_flag,
        "ml_anomaly": ml_flag,
        "reference_flag": int(row["reference_flag"]),
        "investigation_reason": str(row.get("investigation_reason", "")),
        "detected_by": detector_names,
        "metric_reasons": metric_reasons,
        "severity": severity,
        "create_issue": severity in {"HIGH", "CRITICAL"},
        "issue_title": issue_title,
        "training_only": True,
    }

def build_incidents(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    incidents = []
    for row in rows:
        event = classify_observation(row)
        if event is not None:
            incidents.append(event)
    return incidents
