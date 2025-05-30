# tree.py (filtered version)
import os

TARGET_DIRS = {"templates", "api", "routes"}

def tree(dir_path: str = ".", prefix: str = ""):
    try:
        items = sorted(os.listdir(dir_path))
    except PermissionError:
        return

    for i, name in enumerate(items):
        full_path = os.path.join(dir_path, name)
        connector = "└── " if i == len(items) - 1 else "├── "

        if os.path.isdir(full_path):
            if name in TARGET_DIRS or dir_path.split("/")[-1] in TARGET_DIRS:
                print(prefix + connector + name + "/")
                extension = "    " if i == len(items) - 1 else "│   "
                tree(full_path, prefix + extension)
            else:
                tree(full_path, prefix)
        elif name.endswith(".py") or name.endswith(".html"):
            print(prefix + connector + name)

if __name__ == "__main__":
    tree()
