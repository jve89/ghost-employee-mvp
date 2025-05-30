import os
from collections import defaultdict

# Keywords to scan for overlaps
KEYWORDS = ["retry", "summary", "task", "log", "export", "template", "report", "email", "schedule"]

def scan_py_files(base_dir="."):
    clusters = defaultdict(list)
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                for key in KEYWORDS:
                    if key in file:
                        clusters[key].append(os.path.join(root, file))
    return clusters

def describe_file(filename):
    # Very basic purpose guesser
    name = os.path.basename(filename)
    if "test" in name:
        return "Test case"
    if "api" in name:
        return "API endpoint"
    if "worker" in name:
        return "Background process or runner"
    if "manager" in name:
        return "Controller logic or coordination"
    if "utils" in name:
        return "Helper functions"
    if "tile" in name or "dashboard" in name:
        return "Dashboard UI or stats"
    if "export" in name:
        return "Output dispatcher"
    return "Unclassified"

def main():
    clusters = scan_py_files()
    for key, files in sorted(clusters.items()):
        print(f"\n🔹 Cluster: '{key}' ({len(files)} files)\n" + "-"*40)
        for path in sorted(files):
            print(f"🗂  {path}  →  {describe_file(path)}")

if __name__ == "__main__":
    main()
