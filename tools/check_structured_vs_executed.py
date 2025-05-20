import os
import json
import pandas as pd

structured_dir = "logs"
executed_dir = "executed"

# Load structured logs
structured_logs = {}
for f in os.listdir(structured_dir):
    if f.startswith("structured_") and f.endswith(".json"):
        try:
            with open(os.path.join(structured_dir, f), "r") as file:
                data = json.load(file)
                structured_logs[f] = data
        except Exception as e:
            continue

# Load executed logs and match by source_file
matched_logs = []
unmatched_structured = list(structured_logs.keys())

for f in os.listdir(executed_dir):
    if f.startswith("exec_") and f.endswith(".json"):
        try:
            with open(os.path.join(executed_dir, f), "r") as file:
                exec_data = json.load(file)
                source_file = exec_data.get("source_file", "")
                if source_file in structured_logs:
                    matched_logs.append((source_file, f))
                    if source_file in unmatched_structured:
                        unmatched_structured.remove(source_file)
        except Exception:
            continue

# Display results
print("\n✅ Matched structured + executed logs:\n")
for pair in matched_logs:
    print(f"- {pair[0]}  ⇨  {pair[1]}")

if unmatched_structured:
    print("\n🔍 Structured logs with NO matching execution:\n")
    for s in unmatched_structured:
        print(f" - {s}")
else:
    print("\n✅ All structured logs have matching execution entries.")
