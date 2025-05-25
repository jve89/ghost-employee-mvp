# /src/main.py

import os
from src.controller import process_file
from dotenv import load_dotenv
load_dotenv()


WATCHED_DIR = "watched"

def main():
    print("[Main] Starting Ghost Employee task pipeline...")

    for filename in os.listdir(WATCHED_DIR):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(WATCHED_DIR, filename)
        process_file(file_path)

    print("[Main] Task pipeline complete.")

if __name__ == "__main__":
    main()
