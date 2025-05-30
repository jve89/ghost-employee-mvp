import pandas as pd
import os

os.makedirs("sample_inputs", exist_ok=True)

df = pd.DataFrame([
    {"Action": "Follow up with supplier", "Deadline": "2025-06-01", "Priority": "High", "Assigned To": "Alex"},
    {"Action": "Update website pricing", "Deadline": "2025-06-03", "Priority": "Medium", "Assigned To": "Marketing"},
    {"Action": "Prepare training material", "Deadline": "2025-06-07", "Priority": "Low", "Assigned To": "HR"}
])

df.to_excel("sample_inputs/sample_tasks.xlsx", index=False)
print("✅ sample_tasks.xlsx created")
