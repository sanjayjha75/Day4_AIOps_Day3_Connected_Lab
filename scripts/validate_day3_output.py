from pathlib import Path
from incident_logic import load_day3_output

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "day3" / "anomaly_comparison.csv"

rows = load_day3_output(INPUT)
flagged = [r for r in rows if int(r["rule_anomaly"]) == 1 or int(r["ml_anomaly"]) == 1]
print("Day 3 output validation passed")
print(f"Input file: {INPUT}")
print(f"Rows read: {len(rows)}")
print(f"Rows flagged by at least one Day 3 detector: {len(flagged)}")
print("Required columns, numeric measurements, detector flags, and metric ranges are valid.")
